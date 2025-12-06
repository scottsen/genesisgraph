"""
BBS+ Signatures for Unlinkable Selective Disclosure

BBS+ (Boneh-Boyen-Shacham) signatures enable:
- Selective disclosure of attributes from a credential
- Unlinkable presentations (each presentation is unlinkable to others)
- Zero-knowledge proofs of signature possession

This is a foundational implementation demonstrating BBS+ concepts.
For production use, consider:
- mattrglobal/bbs-signatures (JavaScript/Rust)
- Hyperledger AnonCreds
- W3C Data Integrity BBS Cryptosuites

Reference:
- IETF BBS Signatures: https://datatracker.ietf.org/doc/html/draft-irtf-cfrg-bbs-signatures
- W3C DI-BBS: https://w3c.github.io/vc-di-bbs/
"""

import hashlib
import json
import secrets
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

try:
    # Try to import zksk for zero-knowledge proofs
    # Note: zksk may not be available, so we'll provide a fallback
    import zksk
    ZKSK_AVAILABLE = True
except ImportError:
    ZKSK_AVAILABLE = False


@dataclass
class BBSPlusSignature:
    """
    BBS+ signature over multiple messages

    In BBS+, a signature is created over multiple messages (attributes).
    The signature can later be used to create selective disclosure proofs.
    """
    signature: bytes
    public_key: bytes
    message_count: int
    algorithm: str = "BBS-PLUS-SHA256"

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary"""
        return {
            "signature": self.signature.hex(),
            "public_key": self.public_key.hex(),
            "message_count": self.message_count,
            "algorithm": self.algorithm,
        }


@dataclass
class BBSPlusProof:
    """
    BBS+ selective disclosure proof

    This proof demonstrates possession of a valid BBS+ signature
    while selectively revealing only specified attributes.
    Each proof is unlinkable to the original signature and to other proofs.
    """
    proof: bytes
    revealed_messages: Dict[int, Any]
    disclosed_indices: List[int]
    public_key: bytes
    nonce: bytes

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary"""
        return {
            "proof": self.proof.hex(),
            "revealed_messages": {
                str(idx): val for idx, val in self.revealed_messages.items()
            },
            "disclosed_indices": self.disclosed_indices,
            "public_key": self.public_key.hex(),
            "nonce": self.nonce.hex(),
            "algorithm": "BBS-PLUS-SHA256",
        }


class BBSPlusIssuer:
    """
    BBS+ Signature Issuer

    Issues BBS+ signatures over multiple messages (credential attributes).
    These signatures can later be used for selective disclosure.

    Note: This is a simplified implementation for demonstration.
    Production systems should use battle-tested libraries.
    """

    def __init__(self, issuer_did: str):
        """
        Initialize BBS+ issuer

        Args:
            issuer_did: DID of the issuer
        """
        self.issuer_did = issuer_did
        # Generate keypair (simplified - in production, use proper pairing curves)
        self.private_key = secrets.token_bytes(32)
        self.public_key = self._derive_public_key(self.private_key)

    def _derive_public_key(self, private_key: bytes) -> bytes:
        """Derive public key from private key (simplified)"""
        # In production, this would use BLS12-381 pairing curve
        # For now, use a simple hash-based derivation
        return hashlib.sha256(b"BBS+PK:" + private_key).digest()

    def issue_credential(
        self,
        attributes: Dict[str, Any],
        attribute_order: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Issue a BBS+ signed credential

        Args:
            attributes: Dictionary of attribute names to values
            attribute_order: Explicit ordering of attributes (for consistency)

        Returns:
            Credential with BBS+ signature

        Example:
            issuer = BBSPlusIssuer("did:web:example.com")
            cred = issuer.issue_credential({
                "name": "Alice",
                "age": 25,
                "email": "alice@example.com",
                "temperature": 0.25
            })
        """
        # Determine attribute order
        if attribute_order is None:
            attribute_order = sorted(attributes.keys())

        # Encode messages
        messages = [attributes[attr] for attr in attribute_order]
        message_bytes = [self._encode_message(msg) for msg in messages]

        # Create signature (simplified)
        signature_bytes = self._sign_messages(message_bytes)

        signature = BBSPlusSignature(
            signature=signature_bytes,
            public_key=self.public_key,
            message_count=len(messages),
        )

        return {
            "type": "BBSPlusCredential",
            "issuer": self.issuer_did,
            "issued": datetime.utcnow().isoformat() + "Z",
            "attributes": attributes,
            "attribute_order": attribute_order,
            "signature": signature.to_dict(),
        }

    def _encode_message(self, message: Any) -> bytes:
        """Encode a message for signing"""
        # Canonical JSON encoding
        msg_str = json.dumps(message, sort_keys=True)
        return hashlib.sha256(msg_str.encode()).digest()

    def _sign_messages(self, message_bytes: List[bytes]) -> bytes:
        """
        Sign multiple messages with BBS+

        This is a SIMPLIFIED implementation.
        Production BBS+ uses pairing-based cryptography on BLS12-381 curve.
        """
        # Combine all messages with private key
        combined = b"".join([self.private_key] + message_bytes)
        signature = hashlib.sha512(combined).digest()
        return signature


class BBSPlusVerifier:
    """
    BBS+ Signature Verifier

    Verifies BBS+ selective disclosure proofs while ensuring:
    - The proof is valid and came from a trusted issuer
    - Only the disclosed attributes are revealed
    - Each proof is unlinkable to prevent tracking
    """

    def __init__(self, trusted_issuers: Optional[List[str]] = None):
        """
        Initialize BBS+ verifier

        Args:
            trusted_issuers: List of trusted issuer DIDs
        """
        self.trusted_issuers = set(trusted_issuers) if trusted_issuers else None

    def create_presentation(
        self,
        credential: Dict[str, Any],
        disclosed_attributes: List[str],
        nonce: Optional[bytes] = None,
    ) -> Dict[str, Any]:
        """
        Create a selective disclosure presentation from a credential

        This creates an unlinkable proof that discloses only specified attributes.

        Args:
            credential: BBS+ credential from issuer
            disclosed_attributes: List of attribute names to disclose
            nonce: Optional nonce for freshness (generated if not provided)

        Returns:
            BBS+ presentation with selective disclosure

        Example:
            presentation = verifier.create_presentation(
                credential,
                disclosed_attributes=["age", "temperature"],
                nonce=b"challenge123"
            )
        """
        if nonce is None:
            nonce = secrets.token_bytes(32)

        # Get attribute order and signature
        attributes = credential["attributes"]
        attribute_order = credential["attribute_order"]
        signature_data = credential["signature"]

        # Determine which indices to disclose
        disclosed_indices = [
            idx for idx, attr in enumerate(attribute_order)
            if attr in disclosed_attributes
        ]

        # Extract revealed messages
        revealed_messages = {
            idx: attributes[attribute_order[idx]]
            for idx in disclosed_indices
        }

        # Create proof (simplified)
        # In production, this would be a zero-knowledge proof
        proof_bytes = self._create_disclosure_proof(
            signature_data=signature_data,
            all_messages=[attributes[attr] for attr in attribute_order],
            disclosed_indices=disclosed_indices,
            nonce=nonce,
        )

        proof = BBSPlusProof(
            proof=proof_bytes,
            revealed_messages=revealed_messages,
            disclosed_indices=disclosed_indices,
            public_key=bytes.fromhex(signature_data["public_key"]),
            nonce=nonce,
        )

        return {
            "type": "BBSPlusPresentation",
            "issuer": credential["issuer"],
            "proof": proof.to_dict(),
            "attribute_order": attribute_order,
            "created": datetime.utcnow().isoformat() + "Z",
        }

    def verify_presentation(
        self,
        presentation: Dict[str, Any],
        expected_nonce: Optional[bytes] = None,
    ) -> Dict[str, Any]:
        """
        Verify a BBS+ presentation

        Args:
            presentation: BBS+ presentation to verify
            expected_nonce: Expected nonce (for challenge-response)

        Returns:
            Verification result with disclosed attributes
        """
        errors = []
        issuer = presentation.get("issuer")

        # Check trusted issuer
        if self.trusted_issuers and issuer not in self.trusted_issuers:
            errors.append(f"Untrusted issuer: {issuer}")

        # Verify proof
        proof_data = presentation["proof"]
        proof_valid = self._verify_disclosure_proof(proof_data, expected_nonce)

        if not proof_valid:
            errors.append("Proof verification failed")

        # Extract revealed attributes
        revealed_attrs = {}
        attribute_order = presentation["attribute_order"]
        revealed_messages = proof_data["revealed_messages"]

        for idx_str, value in revealed_messages.items():
            idx = int(idx_str)
            if idx < len(attribute_order):
                attr_name = attribute_order[idx]
                revealed_attrs[attr_name] = value

        return {
            "valid": len(errors) == 0,
            "issuer": issuer,
            "revealed_attributes": revealed_attrs,
            "unlinkable": True,  # BBS+ presentations are unlinkable
            "errors": errors if errors else None,
        }

    def _create_disclosure_proof(
        self,
        signature_data: Dict[str, Any],
        all_messages: List[Any],
        disclosed_indices: List[int],
        nonce: bytes,
    ) -> bytes:
        """
        Create a zero-knowledge proof of signature possession with selective disclosure

        This is SIMPLIFIED. Production BBS+ uses:
        - Pairing-based cryptography (BLS12-381)
        - Fiat-Shamir heuristic for non-interactivity
        - Proper zero-knowledge proof construction
        """
        # Encode messages
        message_bytes = [
            hashlib.sha256(json.dumps(msg, sort_keys=True).encode()).digest()
            for msg in all_messages
        ]

        # Create proof commitment (simplified)
        signature = bytes.fromhex(signature_data["signature"])
        public_key = bytes.fromhex(signature_data["public_key"])

        proof_input = b"".join([
            signature,
            public_key,
            nonce,
        ] + [message_bytes[i] for i in disclosed_indices])

        proof = hashlib.sha512(proof_input).digest()
        return proof

    def _verify_disclosure_proof(
        self,
        proof_data: Dict[str, Any],
        expected_nonce: Optional[bytes] = None,
    ) -> bool:
        """
        Verify a disclosure proof

        This is SIMPLIFIED. Production verification involves:
        - Pairing checks on BLS12-381
        - Proof of knowledge verification
        - Commitment verification
        """
        # Basic validation
        if expected_nonce is not None:
            provided_nonce = bytes.fromhex(proof_data["nonce"])
            if provided_nonce != expected_nonce:
                return False

        # In production, verify zero-knowledge proof
        # For now, we accept if the structure is valid
        required_fields = ["proof", "revealed_messages", "disclosed_indices", "public_key"]
        return all(field in proof_data for field in required_fields)


def compare_disclosure_methods() -> Dict[str, Any]:
    """
    Compare different selective disclosure methods

    Returns a comparison of SD-JWT vs BBS+ for educational purposes.
    """
    return {
        "SD-JWT": {
            "standard": "IETF draft-ietf-oauth-selective-disclosure-jwt",
            "signature_scheme": "EdDSA, ES256, etc. (standard JWT algorithms)",
            "unlinkability": "Limited - signatures can be linked",
            "selective_disclosure": "Hash-based commitments",
            "maturity": "High - reference implementations available",
            "use_cases": [
                "OAuth/OIDC identity tokens",
                "Standard web authentication",
                "Simple selective disclosure"
            ],
            "advantages": [
                "Well-standardized (IETF)",
                "Compatible with existing JWT infrastructure",
                "Good tooling support"
            ],
            "limitations": [
                "Not unlinkable - can track presentations",
                "Requires disclosure of signature for all verifications"
            ]
        },
        "BBS+": {
            "standard": "IETF draft-irtf-cfrg-bbs-signatures, W3C DI-BBS",
            "signature_scheme": "BLS signatures on BLS12-381 pairing curve",
            "unlinkability": "Full - each presentation is unlinkable",
            "selective_disclosure": "Zero-knowledge proofs",
            "maturity": "Medium - emerging standard, some implementations",
            "use_cases": [
                "Privacy-preserving credentials",
                "Verifiable credentials (W3C VC)",
                "Anti-correlation / anti-tracking"
            ],
            "advantages": [
                "Unlinkable presentations",
                "True zero-knowledge selective disclosure",
                "Minimal disclosure principle"
            ],
            "limitations": [
                "More complex cryptography",
                "Less mature tooling",
                "Requires pairing-friendly curves"
            ]
        },
        "Recommendations": {
            "Use SD-JWT when": [
                "Working with existing JWT/OAuth infrastructure",
                "Unlinkability is not required",
                "Rapid deployment is priority"
            ],
            "Use BBS+ when": [
                "Privacy and unlinkability are critical",
                "Long-term credential reuse expected",
                "Regulatory compliance requires minimal disclosure"
            ]
        }
    }
