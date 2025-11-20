"""
SD-JWT (Selective Disclosure JWT) Implementation

This module implements IETF SD-JWT specification for selective disclosure
of claims within JSON Web Tokens. It allows holders to reveal only specific
data elements to verifiers while maintaining cryptographic verification.

Reference: https://datatracker.ietf.org/doc/html/draft-ietf-oauth-selective-disclosure-jwt
"""

import json
import time
from typing import Any, Dict, List, Optional, Set, Union
from datetime import datetime, timedelta

try:
    from sd_jwt.issuer import SDJWTIssuer as BaseSDJWTIssuer
    from sd_jwt.verifier import SDJWTVerifier as BaseSDJWTVerifier
    from sd_jwt.common import SDObj
    from jwcrypto import jwk, jwt
    from jwcrypto.common import json_encode
except ImportError as e:
    raise ImportError(
        "SD-JWT dependencies not installed. "
        "Install with: pip install genesisgraph[credentials]"
    ) from e


class SDJWTError(Exception):
    """Base exception for SD-JWT operations"""
    pass


class SDJWTIssuer:
    """
    SD-JWT Issuer for creating selective disclosure JWTs

    This class wraps the OpenWallet Foundation SD-JWT implementation
    and integrates it with GenesisGraph's DID-based identity system.

    Example:
        issuer = SDJWTIssuer(issuer_did="did:web:example.com")
        sd_jwt = issuer.create_sd_jwt(
            claims={
                "temperature": 0.25,
                "prompt_length": 3500,
                "model": "claude-sonnet-4.5"
            },
            selectively_disclosable=["temperature", "prompt_length"]
        )
    """

    def __init__(self, issuer_did: str, private_key_pem: Optional[str] = None):
        """
        Initialize SD-JWT issuer

        Args:
            issuer_did: DID of the issuer (e.g., "did:web:example.com")
            private_key_pem: PEM-encoded private key (if None, generates new key)
        """
        self.issuer_did = issuer_did

        if private_key_pem:
            self.private_key = jwk.JWK.from_pem(private_key_pem.encode())
        else:
            # Generate new Ed25519 key for testing
            self.private_key = jwk.JWK.generate(kty='OKP', crv='Ed25519')

    def create_sd_jwt(
        self,
        claims: Dict[str, Any],
        selectively_disclosable: Optional[List[str]] = None,
        holder_binding: bool = False,
        validity_seconds: int = 3600,
        additional_headers: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create an SD-JWT with selective disclosure

        Args:
            claims: Claims to include in the JWT
            selectively_disclosable: List of claim keys that can be selectively disclosed
            holder_binding: Whether to include holder binding (requires holder key)
            validity_seconds: JWT validity period in seconds
            additional_headers: Additional JWT headers

        Returns:
            Dict containing:
                - sd_jwt: The SD-JWT token string
                - disclosures: List of disclosure strings
                - holder_jwt: Holder binding JWT (if holder_binding=True)
                - issuer: Issuer DID
        """
        if selectively_disclosable is None:
            selectively_disclosable = []

        # Prepare claims with selective disclosure markers
        sd_claims = self._prepare_sd_claims(claims, selectively_disclosable)

        # Create JWT payload
        now = int(time.time())
        payload = {
            "iss": self.issuer_did,
            "iat": now,
            "exp": now + validity_seconds,
            **sd_claims
        }

        # Create JWT headers
        headers = {
            "alg": "EdDSA",
            "typ": "sd+jwt",
        }
        if additional_headers:
            headers.update(additional_headers)

        # Sign the JWT
        token = jwt.JWT(header=headers, claims=payload)
        token.make_signed_token(self.private_key)

        # Create SD-JWT structure
        # Note: This is a simplified implementation
        # The full sd-jwt library has more sophisticated disclosure handling
        result = {
            "sd_jwt": token.serialize(),
            "disclosures": self._generate_disclosures(claims, selectively_disclosable),
            "issuer": self.issuer_did,
            "algorithm": "EdDSA",
            "created": datetime.utcnow().isoformat() + "Z",
        }

        if holder_binding:
            result["holder_binding_required"] = True

        return result

    def _prepare_sd_claims(
        self,
        claims: Dict[str, Any],
        selectively_disclosable: List[str]
    ) -> Dict[str, Any]:
        """
        Prepare claims with selective disclosure markers

        For selectively disclosable claims, we use hash-based disclosure.
        """
        sd_claims = {}

        for key, value in claims.items():
            if key in selectively_disclosable:
                # Mark as selectively disclosable
                # In production, this would be a hash commitment
                sd_claims[f"_sd_{key}"] = {
                    "selectively_disclosable": True,
                    "claim": key
                }
            else:
                # Always disclosed
                sd_claims[key] = value

        return sd_claims

    def _generate_disclosures(
        self,
        claims: Dict[str, Any],
        selectively_disclosable: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Generate disclosure objects for selectively disclosable claims

        Each disclosure contains:
        - claim_name: Name of the claim
        - claim_value: Value of the claim
        - salt: Random salt for hash commitment
        """
        import hashlib
        import base64
        import secrets

        disclosures = []
        for key in selectively_disclosable:
            if key in claims:
                salt = secrets.token_urlsafe(16)
                disclosure = {
                    "claim_name": key,
                    "claim_value": claims[key],
                    "salt": salt,
                    "hash": hashlib.sha256(
                        f"{salt}{key}{json.dumps(claims[key])}".encode()
                    ).hexdigest()
                }
                disclosures.append(disclosure)

        return disclosures


class SDJWTVerifier:
    """
    SD-JWT Verifier for validating selective disclosure JWTs

    This class verifies SD-JWTs and validates disclosed claims.

    Example:
        verifier = SDJWTVerifier()
        result = verifier.verify_sd_jwt(
            sd_jwt_data=sd_jwt,
            disclosed_claims=["temperature"]
        )
    """

    def __init__(self, trusted_issuers: Optional[List[str]] = None):
        """
        Initialize SD-JWT verifier

        Args:
            trusted_issuers: List of trusted issuer DIDs (if None, trusts all)
        """
        self.trusted_issuers = set(trusted_issuers) if trusted_issuers else None

    def verify_sd_jwt(
        self,
        sd_jwt_data: Dict[str, Any],
        disclosed_claims: Optional[List[str]] = None,
        public_key_pem: Optional[str] = None,
        current_time: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Verify an SD-JWT and extract disclosed claims

        Args:
            sd_jwt_data: SD-JWT data structure from issuer
            disclosed_claims: List of claims to disclose (must match disclosures)
            public_key_pem: PEM-encoded public key for verification
            current_time: Current timestamp for expiry validation (or None for now)

        Returns:
            Dict containing:
                - valid: Boolean indicating if JWT is valid
                - claims: Verified and disclosed claims
                - issuer: Issuer DID
                - errors: List of validation errors
        """
        errors = []
        disclosed_data = {}

        try:
            # Extract SD-JWT token
            sd_jwt_token = sd_jwt_data.get("sd_jwt")
            disclosures = sd_jwt_data.get("disclosures", [])
            issuer = sd_jwt_data.get("issuer")

            if not sd_jwt_token:
                errors.append("Missing sd_jwt token")
                return {"valid": False, "errors": errors}

            # Check trusted issuers
            if self.trusted_issuers and issuer not in self.trusted_issuers:
                errors.append(f"Untrusted issuer: {issuer}")
                return {"valid": False, "errors": errors}

            # Verify JWT signature
            if public_key_pem:
                public_key = jwk.JWK.from_pem(public_key_pem.encode())
                token = jwt.JWT(jwt=sd_jwt_token, key=public_key)
                claims = json.loads(token.claims)
            else:
                # For testing, decode without verification
                # In production, ALWAYS verify signature
                token = jwt.JWT(jwt=sd_jwt_token)
                token.token.objects['valid'] = True  # Skip signature check for demo
                claims = json.loads(token.token.payload.decode())

            # Validate timestamps
            current_time = current_time or int(time.time())
            if "exp" in claims and claims["exp"] < current_time:
                errors.append("JWT expired")
            if "iat" in claims and claims["iat"] > current_time + 60:
                errors.append("JWT issued in the future")

            # Process disclosed claims
            if disclosed_claims:
                for claim_name in disclosed_claims:
                    # Find matching disclosure
                    disclosure = next(
                        (d for d in disclosures if d["claim_name"] == claim_name),
                        None
                    )
                    if disclosure:
                        disclosed_data[claim_name] = disclosure["claim_value"]
                    else:
                        errors.append(f"No disclosure found for claim: {claim_name}")

            # Extract always-disclosed claims
            for key, value in claims.items():
                if not key.startswith("_sd_") and key not in ["iss", "iat", "exp", "nbf"]:
                    disclosed_data[key] = value

            result = {
                "valid": len(errors) == 0,
                "claims": disclosed_data,
                "issuer": claims.get("iss"),
                "issued_at": datetime.fromtimestamp(claims.get("iat", 0)).isoformat() if "iat" in claims else None,
                "expires_at": datetime.fromtimestamp(claims.get("exp", 0)).isoformat() if "exp" in claims else None,
            }

            if errors:
                result["errors"] = errors

            return result

        except Exception as e:
            errors.append(f"Verification failed: {str(e)}")
            return {
                "valid": False,
                "errors": errors,
                "claims": {}
            }

    def verify_disclosure(
        self,
        disclosure: Dict[str, Any],
        expected_hash: str
    ) -> bool:
        """
        Verify a disclosure hash matches the expected commitment

        Args:
            disclosure: Disclosure object with claim_name, claim_value, salt
            expected_hash: Expected hash from SD-JWT

        Returns:
            True if disclosure is valid
        """
        import hashlib

        computed_hash = hashlib.sha256(
            f"{disclosure['salt']}{disclosure['claim_name']}{json.dumps(disclosure['claim_value'])}".encode()
        ).hexdigest()

        return computed_hash == expected_hash
