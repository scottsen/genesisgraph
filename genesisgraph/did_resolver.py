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
from typing import Any, Dict, List, Optional, Tuple
from time import time

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

try:
    import ipaddress
    IPADDRESS_AVAILABLE = True
except ImportError:
    IPADDRESS_AVAILABLE = False

from .errors import ValidationError

# Constants for Ed25519 key handling
ED25519_MULTICODEC_PREFIX = 0xED
ED25519_MULTICODEC_SUFFIX = 0x01
ED25519_KEY_LENGTH = 32
MIN_DECODED_LENGTH = 2

# Security: SSRF Protection - Blocked hosts and networks
BLOCKED_HOSTS = {
    'localhost', '127.0.0.1', '0.0.0.0',  # nosec B104 - This is a blocklist for SSRF protection, not binding
    '169.254.169.254',  # AWS metadata service
    '::1',  # IPv6 localhost
    '::ffff:127.0.0.1',  # IPv4-mapped IPv6 localhost
}

# Private network ranges to block
BLOCKED_NETWORKS = [
    '10.0.0.0/8',      # Private network (Class A)
    '172.16.0.0/12',   # Private network (Class B)
    '192.168.0.0/16',  # Private network (Class C)
    '169.254.0.0/16',  # Link-local addresses
    '127.0.0.0/8',     # Loopback
    'fc00::/7',        # IPv6 Unique Local Addresses
    'fe80::/10',       # IPv6 Link-Local addresses
    '::1/128',         # IPv6 loopback
]

# Security: Input size limits
MAX_BASE58_LENGTH = 128  # Maximum base58 string length to prevent DoS
MAX_DID_LENGTH = 512     # Maximum DID length
MAX_RESPONSE_SIZE = 1_000_000  # 1MB max for DID documents


class DIDResolver:
    """
    Resolves DIDs to public keys

    Example:
        >>> resolver = DIDResolver()
        >>> public_key = resolver.resolve_to_public_key("did:key:z6Mk...")
        >>> # Use public_key for signature verification
    """

    def __init__(self, timeout: int = 10, cache_ttl: int = 300, rate_limit: int = 10):
        """
        Initialize DID resolver

        Args:
            timeout: HTTP request timeout in seconds (for did:web)
            cache_ttl: Cache time-to-live in seconds
            rate_limit: Maximum requests per minute per domain (for did:web)
        """
        self.timeout = timeout
        self.cache_ttl = cache_ttl
        self._cache: Dict[str, Tuple[bytes, float]] = {}  # (value, timestamp)
        self._rate_limits: Dict[str, List[float]] = {}  # domain -> list of request timestamps
        self._rate_limit_max = rate_limit

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
        # Security: Validate DID length to prevent DoS
        if len(did) > MAX_DID_LENGTH:
            raise ValidationError(f"DID too long: {len(did)} (max {MAX_DID_LENGTH})")

        # Check cache with TTL
        cache_key = f"{did}#{key_id}" if key_id else did
        if cache_key in self._cache:
            cached_value, cached_time = self._cache[cache_key]
            # Check if cache entry is still valid
            if time() - cached_time < self.cache_ttl:
                return cached_value
            else:
                # Expired - remove from cache
                del self._cache[cache_key]

        # Extract DID method
        if not did.startswith('did:'):
            raise ValidationError(f"Invalid DID format: {did}")

        parts = did.split(':', 2)
        min_did_parts = 3  # did:method:identifier
        if len(parts) < min_did_parts:
            raise ValidationError(f"Invalid DID format: {did}")

        method = parts[1]

        # Route to appropriate resolver
        if method == 'key':
            public_key = self._resolve_did_key(did)
        elif method == 'web':
            public_key = self._resolve_did_web(did, key_id)
        else:
            raise ValidationError(f"Unsupported DID method: {method}")

        # Cache result with timestamp
        self._cache[cache_key] = (public_key, time())

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
            raise ValidationError(f"Failed to decode did:key: {e}") from e

        # Check multicodec prefix for Ed25519 public key
        # Ed25519 public key multicodec: 0xed01 (variable length encoded)
        # In practice, it's encoded as 0xed 0x01 in the byte stream
        if len(decoded) < MIN_DECODED_LENGTH:
            raise ValidationError(f"did:key too short: {len(decoded)} bytes")

        # Expected format: [0xed, 0x01, ...32 bytes of key...]
        if decoded[0] != ED25519_MULTICODEC_PREFIX or decoded[1] != ED25519_MULTICODEC_SUFFIX:
            raise ValidationError(
                f"Unsupported key type in did:key. Expected Ed25519 (0xed01), "
                f"got 0x{decoded[0]:02x}{decoded[1]:02x}"
            )

        # Extract 32-byte Ed25519 public key
        key_start = MIN_DECODED_LENGTH
        key_end = key_start + ED25519_KEY_LENGTH
        public_key = decoded[key_start:key_end]
        if len(public_key) != ED25519_KEY_LENGTH:
            raise ValidationError(
                f"Invalid Ed25519 key length: {len(public_key)} (expected {ED25519_KEY_LENGTH})"
            )

        return public_key

    def _is_blocked_host(self, domain: str) -> bool:
        """
        Check if a domain/host is blocked for security reasons

        Args:
            domain: Domain name or IP address to check

        Returns:
            True if blocked, False if allowed
        """
        # Check against blocked hostnames
        if domain.lower() in BLOCKED_HOSTS:
            return True

        # Check if it's an IP address in a blocked network
        if IPADDRESS_AVAILABLE:
            try:
                ip = ipaddress.ip_address(domain)
                for network_str in BLOCKED_NETWORKS:
                    network = ipaddress.ip_network(network_str)
                    if ip in network:
                        return True
            except ValueError:
                # Not an IP address, domain name is OK (will be resolved by DNS)
                pass

        return False

    def _check_rate_limit(self, domain: str) -> None:
        """
        Enforce rate limiting per domain to prevent abuse

        Args:
            domain: Domain to check rate limit for

        Raises:
            ValidationError: If rate limit is exceeded
        """
        now = time()
        minute_ago = now - 60

        # Initialize rate limit tracking for this domain
        if domain not in self._rate_limits:
            self._rate_limits[domain] = []

        # Clean old requests (older than 1 minute)
        self._rate_limits[domain] = [
            t for t in self._rate_limits[domain] if t > minute_ago
        ]

        # Check if rate limit exceeded
        if len(self._rate_limits[domain]) >= self._rate_limit_max:
            raise ValidationError(
                f"Rate limit exceeded for domain '{domain}': "
                f"{self._rate_limit_max} requests per minute maximum"
            )

        # Record this request
        self._rate_limits[domain].append(now)

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

        Security:
            - Blocks private/internal IP addresses (SSRF protection)
            - Enforces TLS certificate validation
            - Blocks redirects
            - Validates Content-Type and response size
            - Implements rate limiting per domain
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

        # Security: Block dangerous hosts (SSRF protection)
        if self._is_blocked_host(domain):
            raise ValidationError(
                f"Blocked host in did:web for security reasons: {domain}. "
                f"Private/internal hosts are not allowed."
            )

        # Security: Enforce rate limiting
        self._check_rate_limit(domain)

        # Construct URL (always HTTPS for security)
        # If no path: https://example.com/.well-known/did.json
        # If path: https://example.com/path/components/did.json
        if path_parts:
            url = f"https://{domain}/{'/'.join(path_parts)}/did.json"
        else:
            url = f"https://{domain}/.well-known/did.json"

        # Fetch DID document with security controls
        try:
            response = requests.get(
                url,
                timeout=self.timeout,
                verify=True,  # Enforce TLS certificate validation
                allow_redirects=False,  # Prevent redirect-based SSRF
                headers={
                    'Accept': 'application/json',
                    'User-Agent': 'GenesisGraph-DID-Resolver/0.1.0'
                }
            )
            response.raise_for_status()

            # Security: Validate Content-Type
            content_type = response.headers.get('Content-Type', '')
            if 'application/json' not in content_type and 'application/did+json' not in content_type:
                raise ValidationError(
                    f"Invalid content type from {url}: {content_type}. "
                    f"Expected application/json or application/did+json"
                )

            # Security: Validate response size
            if len(response.content) > MAX_RESPONSE_SIZE:
                raise ValidationError(
                    f"Response too large from {url}: {len(response.content)} bytes "
                    f"(max {MAX_RESPONSE_SIZE})"
                )

            did_document = response.json()

        except requests.RequestException as e:
            raise ValidationError(f"Failed to fetch did:web document from {url}: {e}") from e
        except json.JSONDecodeError as e:
            raise ValidationError(f"Invalid JSON in did:web document from {url}: {e}") from e

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

                if 'publicKeyMultibase' in method:
                    multibase = method['publicKeyMultibase']
                    if multibase.startswith('z'):
                        return self._base58_decode(multibase[1:])
                    raise ValidationError(f"Unsupported multibase encoding: {multibase[0]}")

                if 'publicKeyJwk' in method:
                    jwk = method['publicKeyJwk']
                    if jwk.get('kty') != 'OKP' or jwk.get('crv') != 'Ed25519':
                        raise ValidationError(f"Unsupported JWK key type: {jwk}")

                    # Decode base64url-encoded x coordinate
                    x_b64 = jwk.get('x', '')
                    # Add padding if needed
                    x_b64 += '=' * (4 - len(x_b64) % 4)
                    return base64.urlsafe_b64decode(x_b64)

                raise ValidationError("No supported public key format found in verification method")

        raise ValidationError(f"Key {key_id} not found in DID document")

    @staticmethod
    def _base58_decode(s: str) -> bytes:
        """
        Decode base58btc string to bytes with size limits for security

        Args:
            s: Base58btc encoded string

        Returns:
            Decoded bytes

        Raises:
            ValueError: If input is too long or decoded value is too large

        Security:
            - Limits input size to prevent DoS attacks
            - Validates decoded size to prevent integer overflow
        """
        # Security: Limit input size to prevent DoS
        if len(s) > MAX_BASE58_LENGTH:
            raise ValueError(f"Base58 string too long: {len(s)} (max {MAX_BASE58_LENGTH})")

        # Bitcoin-style base58 alphabet
        ALPHABET = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'

        # Convert base58 string to integer
        num = 0
        for char in s:
            if char not in ALPHABET:
                raise ValueError(f"Invalid base58 character: {char}")
            num = num * 58 + ALPHABET.index(char)

        # Security: Sanity check decoded size (prevent integer overflow)
        # Max reasonable size for a key is ~1024 bits = 128 bytes
        max_bit_length = 1024
        if num.bit_length() > max_bit_length:
            raise ValueError(f"Decoded base58 value too large: {num.bit_length()} bits (max {max_bit_length})")

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
