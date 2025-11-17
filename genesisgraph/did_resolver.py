"""
DID Resolution for GenesisGraph

Resolves Decentralized Identifiers (DIDs) to public keys for signature verification.

Supported DID methods:
- did:key - Self-describing cryptographic keys (no resolution needed)
- did:web - Web-based DIDs (resolves via HTTPS)

References:
- W3C DID Core: https://www.w3.org/TR/did-core/
- did:key Method: https://w3c-ccg.github.io/did-method-key/
- did:web Method: https://w3c-ccg.github.io/did-method-web/
"""

import base64
import json
import re
from typing import Optional, Dict, Any
from urllib.parse import urlparse

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

from cryptography.hazmat.primitives.asymmetric import ed25519

from .errors import ValidationError


class DIDResolver:
    """
    Resolves DIDs to public keys

    Example:
        >>> resolver = DIDResolver()
        >>> public_key = resolver.resolve_to_public_key("did:key:z6Mk...")
        >>> # Use public_key for signature verification
    """

    def __init__(self, timeout: int = 10, cache_ttl: int = 300):
        """
        Initialize DID resolver

        Args:
            timeout: HTTP request timeout in seconds (for did:web)
            cache_ttl: Cache time-to-live in seconds
        """
        self.timeout = timeout
        self.cache_ttl = cache_ttl
        self._cache: Dict[str, Any] = {}

    def resolve_to_public_key(self, did: str, key_id: Optional[str] = None) -> bytes:
        """
        Resolve DID to Ed25519 public key bytes

        Args:
            did: Decentralized Identifier (e.g., "did:key:z6Mk...")
            key_id: Optional key identifier for DIDs with multiple keys

        Returns:
            Raw Ed25519 public key bytes (32 bytes)

        Raises:
            ValidationError: If DID resolution fails or key extraction fails

        Example:
            >>> resolver = DIDResolver()
            >>> pub_key = resolver.resolve_to_public_key("did:key:z6MkhaXgBZDvotDkL5257faiztiGiC2QtKLGpbnnEGta2doK")
        """
        # Check cache
        cache_key = f"{did}#{key_id}" if key_id else did
        if cache_key in self._cache:
            return self._cache[cache_key]

        # Extract DID method
        if not did.startswith('did:'):
            raise ValidationError(f"Invalid DID format: {did}")

        parts = did.split(':', 2)
        if len(parts) < 3:
            raise ValidationError(f"Invalid DID format: {did}")

        method = parts[1]

        # Route to appropriate resolver
        if method == 'key':
            public_key = self._resolve_did_key(did)
        elif method == 'web':
            public_key = self._resolve_did_web(did, key_id)
        else:
            raise ValidationError(f"Unsupported DID method: {method}")

        # Cache result
        self._cache[cache_key] = public_key

        return public_key

    def _resolve_did_key(self, did: str) -> bytes:
        """
        Resolve did:key (self-describing key)

        Format: did:key:z<multibase-multicodec-encoded-key>

        Example: did:key:z6MkhaXgBZDvotDkL5257faiztiGiC2QtKLGpbnnEGta2doK

        Args:
            did: did:key identifier

        Returns:
            Ed25519 public key bytes

        Raises:
            ValidationError: If key format is invalid
        """
        # Extract multibase string (everything after "did:key:")
        if not did.startswith('did:key:'):
            raise ValidationError(f"Invalid did:key format: {did}")

        multibase_key = did[8:]  # Skip "did:key:"

        # Check multibase encoding (z = base58btc)
        if not multibase_key.startswith('z'):
            raise ValidationError(f"Unsupported multibase encoding in did:key: {multibase_key[0]}")

        # Decode base58btc
        try:
            decoded = self._base58_decode(multibase_key[1:])  # Skip 'z'
        except Exception as e:
            raise ValidationError(f"Failed to decode did:key: {e}")

        # Check multicodec prefix for Ed25519 public key
        # Ed25519 public key multicodec: 0xed01 (variable length encoded)
        # In practice, it's encoded as 0xed 0x01 in the byte stream
        if len(decoded) < 2:
            raise ValidationError(f"did:key too short: {len(decoded)} bytes")

        # Expected format: [0xed, 0x01, ...32 bytes of key...]
        if decoded[0] != 0xed or decoded[1] != 0x01:
            raise ValidationError(
                f"Unsupported key type in did:key. Expected Ed25519 (0xed01), "
                f"got 0x{decoded[0]:02x}{decoded[1]:02x}"
            )

        # Extract 32-byte Ed25519 public key
        public_key = decoded[2:34]
        if len(public_key) != 32:
            raise ValidationError(f"Invalid Ed25519 key length: {len(public_key)} (expected 32)")

        return public_key

    def _resolve_did_web(self, did: str, key_id: Optional[str] = None) -> bytes:
        """
        Resolve did:web by fetching DID document via HTTPS

        Format: did:web:example.com
                did:web:example.com:user:alice

        Resolves to: https://example.com/.well-known/did.json
                     https://example.com/user/alice/did.json

        Args:
            did: did:web identifier
            key_id: Optional key identifier (e.g., "#key-1")

        Returns:
            Ed25519 public key bytes

        Raises:
            ValidationError: If resolution fails or key extraction fails
        """
        if not REQUESTS_AVAILABLE:
            raise ValidationError("did:web resolution requires 'requests' library")

        if not did.startswith('did:web:'):
            raise ValidationError(f"Invalid did:web format: {did}")

        # Extract domain and path
        # Format: did:web:example.com[:path:components]
        parts = did[8:].split(':')  # Skip "did:web:"
        domain = parts[0]
        path_parts = parts[1:] if len(parts) > 1 else []

        # Construct URL
        # If no path: https://example.com/.well-known/did.json
        # If path: https://example.com/path/components/did.json
        if path_parts:
            url = f"https://{domain}/{'/'.join(path_parts)}/did.json"
        else:
            url = f"https://{domain}/.well-known/did.json"

        # Fetch DID document
        try:
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            did_document = response.json()
        except requests.RequestException as e:
            raise ValidationError(f"Failed to fetch did:web document from {url}: {e}")
        except json.JSONDecodeError as e:
            raise ValidationError(f"Invalid JSON in did:web document from {url}: {e}")

        # Extract public key from DID document
        return self._extract_public_key_from_document(did_document, key_id or "#keys-1")

    def _extract_public_key_from_document(self, did_document: Dict, key_id: str) -> bytes:
        """
        Extract Ed25519 public key from DID document

        Supports:
        - verificationMethod with publicKeyBase58
        - verificationMethod with publicKeyMultibase
        - verificationMethod with publicKeyJwk

        Args:
            did_document: Parsed DID document
            key_id: Key identifier (e.g., "#keys-1")

        Returns:
            Ed25519 public key bytes

        Raises:
            ValidationError: If key not found or unsupported format
        """
        # Look in verificationMethod array
        verification_methods = did_document.get('verificationMethod', [])

        for method in verification_methods:
            # Match key by id (can be relative "#keys-1" or absolute "did:web:example.com#keys-1")
            method_id = method.get('id', '')
            if method_id == key_id or method_id.endswith(key_id):
                # Check key type
                key_type = method.get('type')
                if key_type not in ['Ed25519VerificationKey2018', 'Ed25519VerificationKey2020',
                                    'JsonWebKey2020']:
                    raise ValidationError(f"Unsupported key type: {key_type}")

                # Extract key based on format
                if 'publicKeyBase58' in method:
                    key_b58 = method['publicKeyBase58']
                    return self._base58_decode(key_b58)

                elif 'publicKeyMultibase' in method:
                    multibase = method['publicKeyMultibase']
                    if multibase.startswith('z'):
                        return self._base58_decode(multibase[1:])
                    else:
                        raise ValidationError(f"Unsupported multibase encoding: {multibase[0]}")

                elif 'publicKeyJwk' in method:
                    jwk = method['publicKeyJwk']
                    if jwk.get('kty') != 'OKP' or jwk.get('crv') != 'Ed25519':
                        raise ValidationError(f"Unsupported JWK key type: {jwk}")

                    # Decode base64url-encoded x coordinate
                    x_b64 = jwk.get('x', '')
                    # Add padding if needed
                    x_b64 += '=' * (4 - len(x_b64) % 4)
                    return base64.urlsafe_b64decode(x_b64)

                else:
                    raise ValidationError(f"No supported public key format found in verification method")

        raise ValidationError(f"Key {key_id} not found in DID document")

    @staticmethod
    def _base58_decode(s: str) -> bytes:
        """
        Decode base58btc string to bytes

        Args:
            s: Base58btc encoded string

        Returns:
            Decoded bytes
        """
        # Bitcoin-style base58 alphabet
        ALPHABET = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'

        # Convert base58 string to integer
        num = 0
        for char in s:
            if char not in ALPHABET:
                raise ValueError(f"Invalid base58 character: {char}")
            num = num * 58 + ALPHABET.index(char)

        # Convert integer to bytes
        # Count leading zeros
        leading_zeros = len(s) - len(s.lstrip('1'))

        # Convert number to bytes
        if num == 0:
            return b'\x00' * leading_zeros

        bytes_list = []
        while num > 0:
            num, remainder = divmod(num, 256)
            bytes_list.insert(0, remainder)

        # Add leading zero bytes
        return b'\x00' * leading_zeros + bytes(bytes_list)

    def clear_cache(self):
        """Clear the DID resolution cache"""
        self._cache.clear()


def resolve_did_to_public_key(did: str, key_id: Optional[str] = None) -> bytes:
    """
    Convenience function to resolve DID to Ed25519 public key

    Args:
        did: Decentralized Identifier
        key_id: Optional key identifier

    Returns:
        Raw Ed25519 public key bytes (32 bytes)

    Raises:
        ValidationError: If resolution fails

    Example:
        >>> from genesisgraph.did_resolver import resolve_did_to_public_key
        >>> pub_key = resolve_did_to_public_key("did:key:z6MkhaXgBZDvotDkL5257faiztiGiC2QtKLGpbnnEGta2doK")
    """
    resolver = DIDResolver()
    return resolver.resolve_to_public_key(did, key_id)
