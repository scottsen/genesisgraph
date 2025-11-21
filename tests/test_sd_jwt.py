"""
Tests for SD-JWT (Selective Disclosure JWT) implementation

Tests cover:
- SD-JWT creation and verification
- Selective disclosure of claims
- Integration with GenesisGraph attestations
- Security and error handling
"""

import pytest
import time
from datetime import datetime, timedelta

# Test if credentials module is available
try:
    from genesisgraph.credentials.sd_jwt import SDJWTIssuer, SDJWTVerifier, SDJWTError
    from jwcrypto import jwk
    CREDENTIALS_AVAILABLE = True
except ImportError:
    CREDENTIALS_AVAILABLE = False
    pytest.skip("Credentials module not available. Install with: pip install genesisgraph[credentials]", allow_module_level=True)


class TestSDJWTIssuer:
    """Test SD-JWT issuer functionality"""

    def test_create_issuer(self):
        """Test creating an SD-JWT issuer"""
        issuer = SDJWTIssuer(issuer_did="did:web:example.com")
        assert issuer.issuer_did == "did:web:example.com"
        assert issuer.private_key is not None

    def test_create_sd_jwt_basic(self):
        """Test creating a basic SD-JWT with selective disclosure"""
        issuer = SDJWTIssuer(issuer_did="did:web:example.com")

        claims = {
            "temperature": 0.25,
            "prompt_length": 3500,
            "model": "claude-sonnet-4.5"
        }

        sd_jwt = issuer.create_sd_jwt(
            claims=claims,
            selectively_disclosable=["temperature", "prompt_length"]
        )

        # Verify structure
        assert "sd_jwt" in sd_jwt
        assert "disclosures" in sd_jwt
        assert "issuer" in sd_jwt
        assert sd_jwt["issuer"] == "did:web:example.com"
        assert len(sd_jwt["disclosures"]) == 2  # temperature and prompt_length

    def test_create_sd_jwt_no_selective_disclosure(self):
        """Test creating SD-JWT with all claims always disclosed"""
        issuer = SDJWTIssuer(issuer_did="did:web:example.com")

        claims = {
            "model": "claude-sonnet-4.5",
            "temperature": 0.25
        }

        sd_jwt = issuer.create_sd_jwt(
            claims=claims,
            selectively_disclosable=[]  # No selective disclosure
        )

        assert "sd_jwt" in sd_jwt
        assert len(sd_jwt["disclosures"]) == 0

    def test_create_sd_jwt_with_holder_binding(self):
        """Test creating SD-JWT with holder binding"""
        issuer = SDJWTIssuer(issuer_did="did:web:example.com")

        claims = {"temperature": 0.25}

        sd_jwt = issuer.create_sd_jwt(
            claims=claims,
            selectively_disclosable=["temperature"],
            holder_binding=True
        )

        assert sd_jwt.get("holder_binding_required") is True

    def test_disclosure_structure(self):
        """Test that disclosures have correct structure"""
        issuer = SDJWTIssuer(issuer_did="did:web:example.com")

        claims = {"temperature": 0.25, "prompt_length": 3500}

        sd_jwt = issuer.create_sd_jwt(
            claims=claims,
            selectively_disclosable=["temperature"]
        )

        disclosures = sd_jwt["disclosures"]
        assert len(disclosures) == 1

        disclosure = disclosures[0]
        assert "claim_name" in disclosure
        assert "claim_value" in disclosure
        assert "salt" in disclosure
        assert "hash" in disclosure
        assert disclosure["claim_name"] == "temperature"
        assert disclosure["claim_value"] == 0.25


class TestSDJWTVerifier:
    """Test SD-JWT verifier functionality"""

    def test_create_verifier(self):
        """Test creating an SD-JWT verifier"""
        verifier = SDJWTVerifier()
        assert verifier.trusted_issuers is None

        verifier_with_trust = SDJWTVerifier(trusted_issuers=["did:web:example.com"])
        assert "did:web:example.com" in verifier_with_trust.trusted_issuers

    def test_verify_sd_jwt_basic(self):
        """Test verifying a valid SD-JWT"""
        issuer = SDJWTIssuer(issuer_did="did:web:example.com")
        claims = {
            "temperature": 0.25,
            "model": "claude-sonnet-4.5"
        }

        sd_jwt = issuer.create_sd_jwt(
            claims=claims,
            selectively_disclosable=["temperature"]
        )

        verifier = SDJWTVerifier()
        result = verifier.verify_sd_jwt(
            sd_jwt_data=sd_jwt,
            disclosed_claims=["temperature"]
        )

        assert result["valid"] is True
        assert "temperature" in result["claims"]
        assert result["claims"]["temperature"] == 0.25
        assert result["issuer"] == "did:web:example.com"

    def test_verify_sd_jwt_partial_disclosure(self):
        """Test verifying SD-JWT with partial claim disclosure"""
        issuer = SDJWTIssuer(issuer_did="did:web:example.com")
        claims = {
            "temperature": 0.25,
            "prompt_length": 3500,
            "model": "claude-sonnet-4.5"  # Always disclosed
        }

        sd_jwt = issuer.create_sd_jwt(
            claims=claims,
            selectively_disclosable=["temperature", "prompt_length"]
        )

        verifier = SDJWTVerifier()

        # Disclose only temperature, not prompt_length
        result = verifier.verify_sd_jwt(
            sd_jwt_data=sd_jwt,
            disclosed_claims=["temperature"]
        )

        assert result["valid"] is True
        assert "temperature" in result["claims"]
        assert result["claims"]["temperature"] == 0.25
        assert "prompt_length" not in result["claims"]  # Not disclosed
        assert "model" in result["claims"]  # Always disclosed

    def test_verify_sd_jwt_untrusted_issuer(self):
        """Test that untrusted issuers are rejected"""
        issuer = SDJWTIssuer(issuer_did="did:web:untrusted.com")
        claims = {"temperature": 0.25}

        sd_jwt = issuer.create_sd_jwt(
            claims=claims,
            selectively_disclosable=["temperature"]
        )

        # Create verifier that only trusts example.com
        verifier = SDJWTVerifier(trusted_issuers=["did:web:example.com"])

        result = verifier.verify_sd_jwt(
            sd_jwt_data=sd_jwt,
            disclosed_claims=["temperature"]
        )

        assert result["valid"] is False
        assert "Untrusted issuer" in str(result.get("errors", []))

    def test_verify_sd_jwt_expired(self):
        """Test that expired JWTs are rejected"""
        issuer = SDJWTIssuer(issuer_did="did:web:example.com")
        claims = {"temperature": 0.25}

        # Create JWT with very short validity
        sd_jwt = issuer.create_sd_jwt(
            claims=claims,
            selectively_disclosable=[],
            validity_seconds=1
        )

        # Wait for expiry
        time.sleep(2)

        verifier = SDJWTVerifier()
        result = verifier.verify_sd_jwt(sd_jwt_data=sd_jwt)

        assert result["valid"] is False
        assert "expired" in str(result.get("errors", [])).lower()

    def test_verify_sd_jwt_missing_disclosure(self):
        """Test that requesting undisclosed claims produces error"""
        issuer = SDJWTIssuer(issuer_did="did:web:example.com")
        claims = {"temperature": 0.25, "prompt_length": 3500}

        sd_jwt = issuer.create_sd_jwt(
            claims=claims,
            selectively_disclosable=["temperature"]
        )

        verifier = SDJWTVerifier()

        # Try to disclose prompt_length which wasn't selectively disclosable
        result = verifier.verify_sd_jwt(
            sd_jwt_data=sd_jwt,
            disclosed_claims=["prompt_length"]
        )

        assert "No disclosure found" in str(result.get("errors", []))


class TestSDJWTIntegration:
    """Test SD-JWT integration with GenesisGraph"""

    def test_genesisgraph_attestation_format(self):
        """Test that SD-JWT can be used in GenesisGraph attestation format"""
        issuer = SDJWTIssuer(issuer_did="did:web:example.com")

        # Create claims about an AI model run
        claims = {
            "model": "claude-sonnet-4.5",
            "temperature": 0.25,
            "max_tokens": 4096,
            "prompt_hash": "sha256:abc123...",
            "output_hash": "sha256:def456..."
        }

        sd_jwt = issuer.create_sd_jwt(
            claims=claims,
            selectively_disclosable=["temperature", "max_tokens"],  # Privacy-sensitive
            validity_seconds=86400  # 24 hours
        )

        # Create GenesisGraph attestation structure
        attestation = {
            "mode": "sd-jwt",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "sd_jwt": sd_jwt
        }

        # Verify structure matches schema
        assert attestation["mode"] == "sd-jwt"
        assert "timestamp" in attestation
        assert "sd_jwt" in attestation
        assert attestation["sd_jwt"]["issuer"] == "did:web:example.com"

    def test_privacy_preserving_workflow(self):
        """Test end-to-end privacy-preserving workflow with SD-JWT"""
        # Step 1: Issuer creates SD-JWT for AI model parameters
        issuer = SDJWTIssuer(issuer_did="did:web:ai-provider.com")

        model_params = {
            "model": "claude-sonnet-4.5",
            "temperature": 0.25,
            "top_p": 0.9,
            "system_prompt_hash": "sha256:secret123"
        }

        sd_jwt = issuer.create_sd_jwt(
            claims=model_params,
            selectively_disclosable=["temperature", "top_p", "system_prompt_hash"]
        )

        # Step 2: Holder decides to disclose only that temperature was used,
        # but not the exact value or other params
        verifier = SDJWTVerifier()

        # Disclose nothing - just prove model was used
        result = verifier.verify_sd_jwt(
            sd_jwt_data=sd_jwt,
            disclosed_claims=[]
        )

        assert result["valid"] is True
        assert "model" in result["claims"]  # Always disclosed
        assert "temperature" not in result["claims"]  # Not disclosed
        assert "top_p" not in result["claims"]  # Not disclosed

        # Step 3: Later, holder decides to also disclose temperature
        result_with_temp = verifier.verify_sd_jwt(
            sd_jwt_data=sd_jwt,
            disclosed_claims=["temperature"]
        )

        assert result_with_temp["valid"] is True
        assert "temperature" in result_with_temp["claims"]
        assert result_with_temp["claims"]["temperature"] == 0.25
        assert "top_p" not in result_with_temp["claims"]  # Still not disclosed


class TestSDJWTSecurity:
    """Security tests for SD-JWT implementation"""

    def test_disclosure_hash_integrity(self):
        """Test that disclosure hashes prevent tampering"""
        issuer = SDJWTIssuer(issuer_did="did:web:example.com")
        verifier = SDJWTVerifier()

        claims = {"temperature": 0.25}

        sd_jwt = issuer.create_sd_jwt(
            claims=claims,
            selectively_disclosable=["temperature"]
        )

        # Get a disclosure and verify its hash
        disclosure = sd_jwt["disclosures"][0]
        result = verifier.verify_disclosure(
            disclosure=disclosure,
            expected_hash=disclosure["hash"]
        )

        assert result is True

        # Try to tamper with the value
        tampered_disclosure = disclosure.copy()
        tampered_disclosure["claim_value"] = 0.9  # Changed!

        result_tampered = verifier.verify_disclosure(
            disclosure=tampered_disclosure,
            expected_hash=disclosure["hash"]
        )

        assert result_tampered is False  # Hash mismatch detects tampering

    def test_different_salt_produces_different_hash(self):
        """Test that salt makes hashes unique"""
        issuer1 = SDJWTIssuer(issuer_did="did:web:example.com")
        issuer2 = SDJWTIssuer(issuer_did="did:web:example.com")

        claims = {"temperature": 0.25}

        sd_jwt1 = issuer1.create_sd_jwt(claims=claims, selectively_disclosable=["temperature"])
        sd_jwt2 = issuer2.create_sd_jwt(claims=claims, selectively_disclosable=["temperature"])

        # Same claim, different issuance = different hashes (due to different salts)
        hash1 = sd_jwt1["disclosures"][0]["hash"]
        hash2 = sd_jwt2["disclosures"][0]["hash"]

        assert hash1 != hash2  # Salts prevent correlation


class TestSDJWTEdgeCases:
    """Test edge cases and error handling"""

    def test_issuer_with_provided_private_key(self):
        """Test creating issuer with provided private key"""
        # Generate a key and export as PEM
        key = jwk.JWK.generate(kty='OKP', crv='Ed25519')
        private_key_pem = key.export_to_pem(private_key=True, password=None).decode()

        # Create issuer with this key
        issuer = SDJWTIssuer(issuer_did="did:web:example.com", private_key_pem=private_key_pem)
        assert issuer.private_key is not None

        # Should be able to create SD-JWT
        claims = {"test": "value"}
        sd_jwt = issuer.create_sd_jwt(claims=claims)
        assert "sd_jwt" in sd_jwt

    def test_create_sd_jwt_with_additional_headers(self):
        """Test creating SD-JWT with additional headers"""
        issuer = SDJWTIssuer(issuer_did="did:web:example.com")

        claims = {"temperature": 0.25}
        additional_headers = {
            "kid": "key-1",
            "custom_field": "custom_value"
        }

        sd_jwt = issuer.create_sd_jwt(
            claims=claims,
            selectively_disclosable=["temperature"],
            additional_headers=additional_headers
        )

        assert "sd_jwt" in sd_jwt
        # Headers are included in the JWT token itself

    def test_create_sd_jwt_with_none_selectively_disclosable(self):
        """Test creating SD-JWT with None as selectively_disclosable"""
        issuer = SDJWTIssuer(issuer_did="did:web:example.com")

        claims = {"temperature": 0.25}

        # Pass None explicitly (though default is None)
        sd_jwt = issuer.create_sd_jwt(
            claims=claims,
            selectively_disclosable=None
        )

        assert "sd_jwt" in sd_jwt
        assert len(sd_jwt["disclosures"]) == 0

    def test_verify_sd_jwt_missing_token(self):
        """Test verification fails when sd_jwt token is missing"""
        verifier = SDJWTVerifier()

        # Create malformed SD-JWT data without token
        malformed_data = {
            "issuer": "did:web:example.com",
            "disclosures": []
            # Missing "sd_jwt" key
        }

        result = verifier.verify_sd_jwt(sd_jwt_data=malformed_data)

        assert result["valid"] is False
        assert "Missing sd_jwt token" in str(result["errors"])

    def test_verify_sd_jwt_with_public_key(self):
        """Test verification with public key"""
        # Create issuer and get keys
        issuer = SDJWTIssuer(issuer_did="did:web:example.com")
        public_key_pem = issuer.private_key.export_to_pem().decode()

        claims = {"temperature": 0.25}
        sd_jwt = issuer.create_sd_jwt(claims=claims, selectively_disclosable=["temperature"])

        # Verify with public key
        verifier = SDJWTVerifier()
        result = verifier.verify_sd_jwt(
            sd_jwt_data=sd_jwt,
            disclosed_claims=["temperature"],
            public_key_pem=public_key_pem
        )

        assert result["valid"] is True
        assert "temperature" in result["claims"]

    def test_verify_sd_jwt_future_issued(self):
        """Test that JWTs issued in the future are rejected"""
        issuer = SDJWTIssuer(issuer_did="did:web:example.com")
        claims = {"temperature": 0.25}

        sd_jwt = issuer.create_sd_jwt(claims=claims)

        verifier = SDJWTVerifier()
        # Use current_time far in the past to make JWT appear issued in future
        result = verifier.verify_sd_jwt(
            sd_jwt_data=sd_jwt,
            current_time=int(time.time()) - 3700  # 1 hour ago
        )

        assert result["valid"] is False
        assert "future" in str(result.get("errors", [])).lower()

    def test_verify_sd_jwt_general_exception(self):
        """Test handling of general exceptions during verification"""
        verifier = SDJWTVerifier()

        # Pass completely invalid data to trigger exception
        invalid_data = {
            "sd_jwt": "not.a.valid.jwt.token.at.all",
            "disclosures": [],
            "issuer": "did:web:example.com"
        }

        result = verifier.verify_sd_jwt(sd_jwt_data=invalid_data)

        assert result["valid"] is False
        assert "Verification failed" in str(result.get("errors", []))


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
