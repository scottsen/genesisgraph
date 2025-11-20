"""
Tests for Predicate Disclosure

Tests cover:
- Creating predicate proofs for privacy-preserving claims
- Verifying predicates without revealing exact values
- Range proofs
- Integration with SD-JWT
"""

import pytest

# Test if credentials module is available
try:
    from genesisgraph.credentials.predicates import (
        PredicateType,
        PredicateProof,
        create_predicate,
        verify_predicate,
        create_range_proof,
        batch_create_predicates,
        combine_with_sd_jwt,
    )
    from genesisgraph.credentials.sd_jwt import SDJWTIssuer
    CREDENTIALS_AVAILABLE = True
except ImportError:
    CREDENTIALS_AVAILABLE = False
    pytest.skip("Credentials module not available. Install with: pip install genesisgraph[credentials]", allow_module_level=True)


class TestPredicateCreation:
    """Test creating predicate proofs"""

    def test_create_less_than_or_equal_proof(self):
        """Test proving temperature <= 0.3 without revealing exact value"""
        proof = create_predicate(
            claim_name="temperature",
            actual_value=0.25,
            predicate_type="lte",
            threshold=0.3,
            disclose_value=False
        )

        assert proof.claim_name == "temperature"
        assert proof.predicate_type == PredicateType.LESS_THAN_OR_EQUAL
        assert proof.threshold == 0.3
        assert proof.satisfied is True  # 0.25 <= 0.3
        assert proof.disclosed_value is None  # Value not disclosed
        assert proof.commitment is not None  # But committed

    def test_create_greater_than_proof(self):
        """Test proving value > threshold"""
        proof = create_predicate(
            claim_name="score",
            actual_value=95,
            predicate_type="gt",
            threshold=80,
            disclose_value=False
        )

        assert proof.satisfied is True  # 95 > 80
        assert proof.disclosed_value is None

    def test_create_proof_with_disclosure(self):
        """Test creating proof that also discloses the value"""
        proof = create_predicate(
            claim_name="temperature",
            actual_value=0.25,
            predicate_type="lte",
            threshold=0.3,
            disclose_value=True  # Disclose exact value
        )

        assert proof.satisfied is True
        assert proof.disclosed_value == 0.25  # Value IS disclosed

    def test_create_failed_predicate(self):
        """Test predicate that is not satisfied"""
        proof = create_predicate(
            claim_name="temperature",
            actual_value=0.8,
            predicate_type="lte",
            threshold=0.3,
            disclose_value=False
        )

        assert proof.satisfied is False  # 0.8 > 0.3, so lte is false

    def test_all_predicate_types(self):
        """Test all supported predicate types"""
        value = 50

        # Less than
        proof_lt = create_predicate("x", value, "lt", 100)
        assert proof_lt.satisfied is True

        # Less than or equal
        proof_lte = create_predicate("x", value, "lte", 50)
        assert proof_lte.satisfied is True

        # Greater than
        proof_gt = create_predicate("x", value, "gt", 25)
        assert proof_gt.satisfied is True

        # Greater than or equal
        proof_gte = create_predicate("x", value, "gte", 50)
        assert proof_gte.satisfied is True

        # Equal
        proof_eq = create_predicate("x", value, "eq", 50)
        assert proof_eq.satisfied is True

        # Not equal
        proof_neq = create_predicate("x", value, "neq", 100)
        assert proof_neq.satisfied is True

        # In set
        proof_in_set = create_predicate("x", value, "in_set", [25, 50, 75])
        assert proof_in_set.satisfied is True


class TestRangeProofs:
    """Test range proofs (proving value is in a range)"""

    def test_create_range_proof_satisfied(self):
        """Test proving value is in range [0.0, 0.3]"""
        proof = create_range_proof(
            claim_name="temperature",
            actual_value=0.25,
            min_value=0.0,
            max_value=0.3,
            disclose_value=False
        )

        assert proof.satisfied is True
        assert proof.predicate_type == PredicateType.IN_RANGE
        assert proof.threshold == (0.0, 0.3)
        assert proof.disclosed_value is None

    def test_create_range_proof_below_range(self):
        """Test proving value below range"""
        proof = create_range_proof(
            claim_name="temperature",
            actual_value=0.25,
            min_value=0.5,
            max_value=1.0,
            disclose_value=False
        )

        assert proof.satisfied is False  # 0.25 not in [0.5, 1.0]

    def test_create_range_proof_above_range(self):
        """Test proving value above range"""
        proof = create_range_proof(
            claim_name="temperature",
            actual_value=0.8,
            min_value=0.0,
            max_value=0.3,
            disclose_value=False
        )

        assert proof.satisfied is False  # 0.8 not in [0.0, 0.3]

    def test_range_proof_boundary_values(self):
        """Test that boundary values are inclusive"""
        # Lower boundary
        proof_min = create_range_proof("x", 0.0, 0.0, 1.0)
        assert proof_min.satisfied is True

        # Upper boundary
        proof_max = create_range_proof("x", 1.0, 0.0, 1.0)
        assert proof_max.satisfied is True


class TestPredicateVerification:
    """Test verifying predicate proofs"""

    def test_verify_valid_proof(self):
        """Test verifying a valid predicate proof"""
        proof = create_predicate(
            claim_name="temperature",
            actual_value=0.25,
            predicate_type="lte",
            threshold=0.3,
            disclose_value=False
        )

        result = verify_predicate(proof)

        assert result["valid"] is True
        assert result["satisfied"] is True
        assert result["claim_name"] == "temperature"

    def test_verify_proof_with_disclosed_value(self):
        """Test verifying proof when value is disclosed"""
        proof = create_predicate(
            claim_name="temperature",
            actual_value=0.25,
            predicate_type="lte",
            threshold=0.3,
            disclose_value=True  # Disclose for verification
        )

        result = verify_predicate(proof, verify_commitment=True)

        assert result["valid"] is True
        assert result["satisfied"] is True
        # Commitment should match disclosed value

    def test_verify_proof_expected_claim_name(self):
        """Test verifying proof with expected claim name"""
        proof = create_predicate(
            claim_name="temperature",
            actual_value=0.25,
            predicate_type="lte",
            threshold=0.3
        )

        # Correct claim name
        result = verify_predicate(proof, expected_claim_name="temperature")
        assert result["valid"] is True

        # Wrong claim name
        result_wrong = verify_predicate(proof, expected_claim_name="humidity")
        assert result_wrong["valid"] is False
        assert "Claim name mismatch" in str(result_wrong.get("errors"))

    def test_verify_tampered_proof(self):
        """Test that tampering is detected"""
        proof = create_predicate(
            claim_name="temperature",
            actual_value=0.25,
            predicate_type="lte",
            threshold=0.3,
            disclose_value=True
        )

        # Tamper with the disclosed value (but keep same commitment)
        proof.disclosed_value = 0.8  # Changed!

        result = verify_predicate(proof, verify_commitment=True)

        # Should detect that disclosed value doesn't match commitment
        assert result["valid"] is False
        assert "does not satisfy claimed predicate" in str(result.get("errors"))


class TestBatchPredicates:
    """Test batch creation of predicate proofs"""

    def test_batch_create_predicates(self):
        """Test creating multiple predicate proofs at once"""
        claims = {
            "temperature": 0.25,
            "prompt_length": 3500,
            "max_tokens": 4096
        }

        predicates = {
            "temperature": {"type": "lte", "threshold": 0.3},
            "prompt_length": {"type": "lte", "threshold": 4000},
            "max_tokens": {"type": "lte", "threshold": 8192}
        }

        proofs = batch_create_predicates(claims, predicates)

        assert len(proofs) == 3
        assert all(proof.satisfied for proof in proofs)
        assert all(proof.disclosed_value is None for proof in proofs)

    def test_batch_create_with_selective_disclosure(self):
        """Test batch creation with some values disclosed"""
        claims = {
            "temperature": 0.25,
            "prompt_length": 3500
        }

        predicates = {
            "temperature": {"type": "lte", "threshold": 0.3},
            "prompt_length": {"type": "lte", "threshold": 4000}
        }

        # Disclose temperature but not prompt_length
        proofs = batch_create_predicates(
            claims,
            predicates,
            disclose_values=["temperature"]
        )

        temp_proof = next(p for p in proofs if p.claim_name == "temperature")
        prompt_proof = next(p for p in proofs if p.claim_name == "prompt_length")

        assert temp_proof.disclosed_value == 0.25  # Disclosed
        assert prompt_proof.disclosed_value is None  # Not disclosed


class TestSDJWTPredicateCombination:
    """Test combining predicates with SD-JWT"""

    def test_combine_predicates_with_sd_jwt(self):
        """Test creating credential with both SD-JWT and predicate proofs"""
        # Create SD-JWT for non-sensitive claims
        issuer = SDJWTIssuer(issuer_did="did:web:example.com")
        claims = {
            "model": "claude-sonnet-4.5",
            "output_hash": "sha256:abc123"
        }

        sd_jwt = issuer.create_sd_jwt(
            claims=claims,
            selectively_disclosable=["output_hash"]
        )

        # Create predicate proofs for sensitive threshold claims
        predicate_claims = {
            "temperature": 0.25,
            "max_tokens": 4096
        }

        predicates = {
            "temperature": {"type": "lte", "threshold": 0.3},
            "max_tokens": {"type": "lte", "threshold": 8192}
        }

        predicate_proofs = batch_create_predicates(predicate_claims, predicates)

        # Combine them
        combined = combine_with_sd_jwt(predicate_proofs, sd_jwt)

        assert combined["type"] == "GenesisGraphCredentialWithPredicates"
        assert "sd_jwt" in combined
        assert "predicate_proofs" in combined
        assert len(combined["predicate_proofs"]) == 2


class TestPredicateSerialization:
    """Test predicate proof serialization"""

    def test_to_dict(self):
        """Test converting predicate proof to dictionary"""
        proof = create_predicate(
            claim_name="temperature",
            actual_value=0.25,
            predicate_type="lte",
            threshold=0.3,
            disclose_value=False
        )

        proof_dict = proof.to_dict()

        assert proof_dict["claim_name"] == "temperature"
        assert proof_dict["predicate"] == "lte"
        assert proof_dict["threshold"] == 0.3
        assert proof_dict["satisfied"] is True
        assert proof_dict["disclosed"] is False
        assert proof_dict["value"] is None

    def test_from_dict(self):
        """Test creating predicate proof from dictionary"""
        proof_dict = {
            "claim_name": "temperature",
            "predicate": "lte",
            "threshold": 0.3,
            "satisfied": True,
            "commitment": "abc123",
            "disclosed": False
        }

        proof = PredicateProof.from_dict(proof_dict)

        assert proof.claim_name == "temperature"
        assert proof.predicate_type == PredicateType.LESS_THAN_OR_EQUAL
        assert proof.threshold == 0.3
        assert proof.satisfied is True

    def test_round_trip_serialization(self):
        """Test round-trip serialization"""
        original = create_predicate(
            claim_name="temperature",
            actual_value=0.25,
            predicate_type="lte",
            threshold=0.3,
            disclose_value=True
        )

        # Convert to dict and back
        as_dict = original.to_dict()
        restored = PredicateProof.from_dict(as_dict)

        assert restored.claim_name == original.claim_name
        assert restored.predicate_type == original.predicate_type
        assert restored.threshold == original.threshold
        assert restored.satisfied == original.satisfied


class TestPredicateUseCases:
    """Real-world use case tests"""

    def test_ai_model_compliance_proof(self):
        """Test proving AI model parameters meet compliance requirements"""
        # Company policy: temperature must be <= 0.3, tokens <= 4000
        actual_params = {
            "temperature": 0.25,
            "max_tokens": 3500,
            "top_p": 0.9
        }

        compliance_requirements = {
            "temperature": {"type": "lte", "threshold": 0.3},
            "max_tokens": {"type": "lte", "threshold": 4000},
            "top_p": {"type": "lte", "threshold": 1.0}
        }

        proofs = batch_create_predicates(actual_params, compliance_requirements)

        # All proofs should be satisfied (compliant)
        assert all(proof.satisfied for proof in proofs)

        # But values are not disclosed (privacy preserved)
        assert all(proof.disclosed_value is None for proof in proofs)

        # Verifier can confirm compliance without knowing exact values
        for proof in proofs:
            result = verify_predicate(proof)
            assert result["valid"] is True
            assert result["satisfied"] is True

    def test_selective_parameter_disclosure(self):
        """Test disclosing some parameters while hiding others"""
        params = {
            "temperature": 0.25,
            "proprietary_param": 42
        }

        predicates = {
            "temperature": {"type": "lte", "threshold": 0.3},
            "proprietary_param": {"type": "lte", "threshold": 100}
        }

        # Disclose temperature (standard) but hide proprietary_param
        proofs = batch_create_predicates(
            params,
            predicates,
            disclose_values=["temperature"]
        )

        temp_proof = next(p for p in proofs if p.claim_name == "temperature")
        prop_proof = next(p for p in proofs if p.claim_name == "proprietary_param")

        # Temperature is disclosed and verifiable
        assert temp_proof.disclosed_value == 0.25
        temp_result = verify_predicate(temp_proof, verify_commitment=True)
        assert temp_result["valid"] is True

        # Proprietary param is proven compliant but value hidden
        assert prop_proof.disclosed_value is None
        assert prop_proof.satisfied is True
        prop_result = verify_predicate(prop_proof)
        assert prop_result["valid"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
