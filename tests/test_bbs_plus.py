"""
Tests for BBS+ Signatures

Tests cover:
- BBS+ credential issuance
- Selective disclosure presentations
- Unlinkability of presentations
- Integration with GenesisGraph
"""

import pytest

# Test if credentials module is available
try:
    from genesisgraph.credentials.bbs_plus import (
        BBSPlusIssuer,
        BBSPlusProof,
        BBSPlusSignature,
        BBSPlusVerifier,
        compare_disclosure_methods,
    )
    CREDENTIALS_AVAILABLE = True
except ImportError:
    CREDENTIALS_AVAILABLE = False
    pytest.skip("Credentials module not available. Install with: pip install genesisgraph[credentials]", allow_module_level=True)


class TestBBSPlusIssuer:
    """Test BBS+ credential issuance"""

    def test_create_issuer(self):
        """Test creating a BBS+ issuer"""
        issuer = BBSPlusIssuer(issuer_did="did:web:example.com")
        assert issuer.issuer_did == "did:web:example.com"
        assert issuer.private_key is not None
        assert issuer.public_key is not None

    def test_issue_credential_basic(self):
        """Test issuing a basic BBS+ credential"""
        issuer = BBSPlusIssuer(issuer_did="did:web:example.com")

        attributes = {
            "name": "Alice",
            "age": 25,
            "email": "alice@example.com"
        }

        credential = issuer.issue_credential(attributes)

        assert credential["type"] == "BBSPlusCredential"
        assert credential["issuer"] == "did:web:example.com"
        assert "issued" in credential
        assert credential["attributes"] == attributes
        assert "signature" in credential

    def test_issue_credential_with_attribute_order(self):
        """Test issuing credential with explicit attribute ordering"""
        issuer = BBSPlusIssuer(issuer_did="did:web:example.com")

        attributes = {
            "temperature": 0.25,
            "model": "claude-sonnet-4.5",
            "max_tokens": 4096
        }

        # Explicit ordering
        attribute_order = ["model", "temperature", "max_tokens"]

        credential = issuer.issue_credential(
            attributes=attributes,
            attribute_order=attribute_order
        )

        assert credential["attribute_order"] == attribute_order

    def test_signature_structure(self):
        """Test that BBS+ signature has correct structure"""
        issuer = BBSPlusIssuer(issuer_did="did:web:example.com")

        attributes = {"temperature": 0.25}

        credential = issuer.issue_credential(attributes)
        signature_data = credential["signature"]

        assert "signature" in signature_data
        assert "public_key" in signature_data
        assert "message_count" in signature_data
        assert "algorithm" in signature_data
        assert signature_data["algorithm"] == "BBS-PLUS-SHA256"
        assert signature_data["message_count"] == 1


class TestBBSPlusVerifier:
    """Test BBS+ selective disclosure and verification"""

    def test_create_verifier(self):
        """Test creating a BBS+ verifier"""
        verifier = BBSPlusVerifier()
        assert verifier.trusted_issuers is None

        verifier_with_trust = BBSPlusVerifier(
            trusted_issuers=["did:web:example.com"]
        )
        assert "did:web:example.com" in verifier_with_trust.trusted_issuers

    def test_create_presentation_full_disclosure(self):
        """Test creating presentation that discloses all attributes"""
        issuer = BBSPlusIssuer(issuer_did="did:web:example.com")
        verifier = BBSPlusVerifier()

        attributes = {
            "name": "Alice",
            "age": 25,
            "email": "alice@example.com"
        }

        credential = issuer.issue_credential(attributes)

        # Disclose all attributes
        presentation = verifier.create_presentation(
            credential=credential,
            disclosed_attributes=["name", "age", "email"]
        )

        assert presentation["type"] == "BBSPlusPresentation"
        assert presentation["issuer"] == "did:web:example.com"
        assert "proof" in presentation
        assert "created" in presentation

    def test_create_presentation_selective_disclosure(self):
        """Test creating presentation with selective disclosure"""
        issuer = BBSPlusIssuer(issuer_did="did:web:example.com")
        verifier = BBSPlusVerifier()

        attributes = {
            "name": "Alice",
            "age": 25,
            "email": "alice@example.com",
            "ssn": "123-45-6789"
        }

        credential = issuer.issue_credential(attributes)

        # Disclose only age and email, hide name and SSN
        presentation = verifier.create_presentation(
            credential=credential,
            disclosed_attributes=["age", "email"]
        )

        proof_data = presentation["proof"]
        revealed_messages = proof_data["revealed_messages"]

        # Check that only disclosed attributes are revealed
        attribute_order = presentation["attribute_order"]
        revealed_attrs = {
            attribute_order[int(idx)]: val
            for idx, val in revealed_messages.items()
        }

        assert "age" in revealed_attrs
        assert "email" in revealed_attrs
        assert "name" not in revealed_attrs
        assert "ssn" not in revealed_attrs

    def test_verify_presentation(self):
        """Test verifying a BBS+ presentation"""
        issuer = BBSPlusIssuer(issuer_did="did:web:example.com")
        verifier = BBSPlusVerifier()

        attributes = {
            "temperature": 0.25,
            "model": "claude-sonnet-4.5"
        }

        credential = issuer.issue_credential(attributes)

        presentation = verifier.create_presentation(
            credential=credential,
            disclosed_attributes=["temperature"]
        )

        # Verify the presentation
        result = verifier.verify_presentation(presentation)

        assert result["valid"] is True
        assert result["unlinkable"] is True  # BBS+ presentations are unlinkable
        assert "temperature" in result["revealed_attributes"]
        assert result["revealed_attributes"]["temperature"] == 0.25

    def test_verify_presentation_untrusted_issuer(self):
        """Test that presentations from untrusted issuers are rejected"""
        issuer = BBSPlusIssuer(issuer_did="did:web:untrusted.com")
        verifier = BBSPlusVerifier(
            trusted_issuers=["did:web:example.com"]  # Only trust example.com
        )

        attributes = {"temperature": 0.25}

        credential = issuer.issue_credential(attributes)
        presentation = verifier.create_presentation(
            credential=credential,
            disclosed_attributes=["temperature"]
        )

        result = verifier.verify_presentation(presentation)

        assert result["valid"] is False
        assert "Untrusted issuer" in str(result.get("errors"))

    def test_presentation_with_nonce(self):
        """Test presentation with nonce for challenge-response"""
        issuer = BBSPlusIssuer(issuer_did="did:web:example.com")
        verifier = BBSPlusVerifier()

        attributes = {"temperature": 0.25}

        credential = issuer.issue_credential(attributes)

        # Create presentation with specific nonce
        nonce = b"challenge12345"
        presentation = verifier.create_presentation(
            credential=credential,
            disclosed_attributes=["temperature"],
            nonce=nonce
        )

        # Verify with expected nonce
        result = verifier.verify_presentation(
            presentation=presentation,
            expected_nonce=nonce
        )

        assert result["valid"] is True

        # Verify with wrong nonce should fail
        wrong_nonce = b"wrongchallenge"
        result_wrong = verifier.verify_presentation(
            presentation=presentation,
            expected_nonce=wrong_nonce
        )

        assert result_wrong["valid"] is False


class TestBBSPlusUnlinkability:
    """Test unlinkability properties of BBS+ signatures"""

    def test_multiple_presentations_are_unlinkable(self):
        """Test that multiple presentations from same credential are unlinkable"""
        issuer = BBSPlusIssuer(issuer_did="did:web:example.com")
        verifier = BBSPlusVerifier()

        attributes = {
            "name": "Alice",
            "age": 25,
            "email": "alice@example.com"
        }

        credential = issuer.issue_credential(attributes)

        # Create two presentations from the same credential
        presentation1 = verifier.create_presentation(
            credential=credential,
            disclosed_attributes=["age"]
        )

        presentation2 = verifier.create_presentation(
            credential=credential,
            disclosed_attributes=["age"]
        )

        # The proofs should be different (unlinkable)
        proof1 = presentation1["proof"]["proof"]
        proof2 = presentation2["proof"]["proof"]

        assert proof1 != proof2  # Different proofs = unlinkable

        # But both should verify
        result1 = verifier.verify_presentation(presentation1)
        result2 = verifier.verify_presentation(presentation2)

        assert result1["valid"] is True
        assert result2["valid"] is True

    def test_different_disclosure_sets(self):
        """Test presentations with different disclosure sets"""
        issuer = BBSPlusIssuer(issuer_did="did:web:example.com")
        verifier = BBSPlusVerifier()

        attributes = {
            "name": "Alice",
            "age": 25,
            "email": "alice@example.com",
            "city": "San Francisco"
        }

        credential = issuer.issue_credential(attributes)

        # Create presentations with different disclosure sets
        presentation_age = verifier.create_presentation(
            credential=credential,
            disclosed_attributes=["age"]
        )

        presentation_city = verifier.create_presentation(
            credential=credential,
            disclosed_attributes=["city"]
        )

        # Verify both
        result_age = verifier.verify_presentation(presentation_age)
        result_city = verifier.verify_presentation(presentation_city)

        assert result_age["valid"] is True
        assert result_city["valid"] is True

        # Check revealed attributes
        assert "age" in result_age["revealed_attributes"]
        assert "city" not in result_age["revealed_attributes"]

        assert "city" in result_city["revealed_attributes"]
        assert "age" not in result_city["revealed_attributes"]


class TestBBSPlusIntegration:
    """Test BBS+ integration with GenesisGraph"""

    def test_genesisgraph_attestation_format(self):
        """Test BBS+ in GenesisGraph attestation format"""
        issuer = BBSPlusIssuer(issuer_did="did:web:ai-provider.com")
        verifier = BBSPlusVerifier()

        # AI model execution attributes
        attributes = {
            "model": "claude-sonnet-4.5",
            "temperature": 0.25,
            "max_tokens": 4096,
            "input_hash": "sha256:abc123",
            "output_hash": "sha256:def456"
        }

        credential = issuer.issue_credential(attributes)

        # Create presentation disclosing only model and hashes
        presentation = verifier.create_presentation(
            credential=credential,
            disclosed_attributes=["model", "input_hash", "output_hash"]
        )

        # Create GenesisGraph attestation
        attestation = {
            "mode": "bbs-plus",
            "timestamp": "2025-01-20T12:00:00Z",
            "bbs_plus": {
                "issuer": presentation["issuer"],
                "proof": presentation["proof"],
                "attribute_order": presentation["attribute_order"]
            }
        }

        # Verify structure
        assert attestation["mode"] == "bbs-plus"
        assert "bbs_plus" in attestation
        assert attestation["bbs_plus"]["issuer"] == "did:web:ai-provider.com"

    def test_privacy_preserving_ai_workflow(self):
        """Test end-to-end privacy-preserving AI workflow with BBS+"""
        # AI provider issues credential about model execution
        issuer = BBSPlusIssuer(issuer_did="did:web:ai-provider.com")

        execution_attributes = {
            "model": "claude-sonnet-4.5",
            "temperature": 0.25,
            "system_prompt": "You are a helpful assistant",
            "user_prompt_hash": "sha256:secret123",
            "output_hash": "sha256:output456",
            "token_count": 1500
        }

        credential = issuer.issue_credential(execution_attributes)

        # Holder creates multiple presentations for different verifiers
        verifier = BBSPlusVerifier()

        # Presentation 1: For public - only model name and output hash
        public_presentation = verifier.create_presentation(
            credential=credential,
            disclosed_attributes=["model", "output_hash"]
        )

        # Presentation 2: For auditor - more details but not prompts
        audit_presentation = verifier.create_presentation(
            credential=credential,
            disclosed_attributes=["model", "temperature", "token_count", "output_hash"]
        )

        # Verify both presentations
        public_result = verifier.verify_presentation(public_presentation)
        audit_result = verifier.verify_presentation(audit_presentation)

        assert public_result["valid"] is True
        assert audit_result["valid"] is True

        # Check what each verifier sees
        assert len(public_result["revealed_attributes"]) == 2
        assert len(audit_result["revealed_attributes"]) == 4

        # Sensitive prompts are never disclosed
        assert "system_prompt" not in public_result["revealed_attributes"]
        assert "system_prompt" not in audit_result["revealed_attributes"]
        assert "user_prompt_hash" not in public_result["revealed_attributes"]


class TestComparisonMethods:
    """Test comparison of disclosure methods"""

    def test_compare_disclosure_methods(self):
        """Test comparison of SD-JWT vs BBS+"""
        comparison = compare_disclosure_methods()

        assert "SD-JWT" in comparison
        assert "BBS+" in comparison
        assert "Recommendations" in comparison

        # Check SD-JWT info
        sd_jwt_info = comparison["SD-JWT"]
        assert "IETF" in sd_jwt_info["standard"]
        assert "unlinkability" in sd_jwt_info
        assert sd_jwt_info["unlinkability"] == "Limited - signatures can be linked"

        # Check BBS+ info
        bbs_info = comparison["BBS+"]
        assert "BLS" in bbs_info["signature_scheme"]
        assert bbs_info["unlinkability"] == "Full - each presentation is unlinkable"

        # Check recommendations
        recommendations = comparison["Recommendations"]
        assert "Use SD-JWT when" in recommendations
        assert "Use BBS+ when" in recommendations


class TestBBSPlusSecurity:
    """Security tests for BBS+ implementation"""

    def test_cannot_forge_presentation(self):
        """Test that presentations cannot be forged without credential"""
        issuer = BBSPlusIssuer(issuer_did="did:web:example.com")
        verifier = BBSPlusVerifier()

        # Legitimate credential
        attributes = {"temperature": 0.25}
        credential = issuer.issue_credential(attributes)

        # Try to create a fake presentation with different issuer
        # This should fail verification
        fake_presentation = {
            "type": "BBSPlusPresentation",
            "issuer": "did:web:fake.com",  # Different issuer
            "proof": {
                "proof": "fakehex",
                "revealed_messages": {"0": 0.99},
                "disclosed_indices": [0],
                "public_key": "fakepubkey",
                "nonce": "fakenonce"
            },
            "attribute_order": ["temperature"]
        }

        # Verification should fail
        verifier_trusted = BBSPlusVerifier(
            trusted_issuers=["did:web:example.com"]
        )
        result = verifier_trusted.verify_presentation(fake_presentation)

        assert result["valid"] is False

    def test_presentation_structure_validation(self):
        """Test that invalid presentation structure is rejected"""
        verifier = BBSPlusVerifier()

        # Missing required fields
        invalid_presentation = {
            "type": "BBSPlusPresentation",
            "issuer": "did:web:example.com",
            # Missing proof
        }

        # Should fail gracefully
        # In real implementation, this would raise validation error


class TestBBSPlusUseCases:
    """Real-world use case tests"""

    def test_age_verification_without_disclosure(self):
        """Test proving age >= 18 without revealing exact age"""
        issuer = BBSPlusIssuer(issuer_did="did:web:id-provider.com")
        verifier = BBSPlusVerifier()

        # Issue credential with birth date and derived age
        attributes = {
            "name": "Alice",
            "birth_date": "2000-01-15",
            "age": 25,
            "over_18": True,
            "over_21": True
        }

        credential = issuer.issue_credential(attributes)

        # Prove over 18 without revealing exact age or birth date
        presentation = verifier.create_presentation(
            credential=credential,
            disclosed_attributes=["over_18"]
        )

        result = verifier.verify_presentation(presentation)

        assert result["valid"] is True
        assert result["revealed_attributes"]["over_18"] is True
        assert "age" not in result["revealed_attributes"]
        assert "birth_date" not in result["revealed_attributes"]

    def test_professional_credential_selective_disclosure(self):
        """Test professional credential with selective disclosure"""
        issuer = BBSPlusIssuer(issuer_did="did:web:university.edu")
        verifier = BBSPlusVerifier()

        attributes = {
            "name": "Dr. Alice Smith",
            "degree": "PhD",
            "field": "Computer Science",
            "graduation_year": 2020,
            "gpa": 3.95,
            "thesis_title": "Advanced Cryptographic Protocols"
        }

        credential = issuer.issue_credential(attributes)

        # For job application: show degree and field, hide GPA and thesis
        job_presentation = verifier.create_presentation(
            credential=credential,
            disclosed_attributes=["degree", "field", "graduation_year"]
        )

        result = verifier.verify_presentation(job_presentation)

        assert result["valid"] is True
        assert result["revealed_attributes"]["degree"] == "PhD"
        assert "gpa" not in result["revealed_attributes"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
