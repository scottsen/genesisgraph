"""
Tests for Zero-Knowledge Proof Templates

Tests comprehensive ZKP template functionality including:
- Range proofs
- Threshold proofs
- Set membership proofs
- Composite proofs
- Template application
- Verification
"""

import pytest

from genesisgraph.credentials.zkp_templates import (
    TemplateType,
    ZKPType,
    apply_template,
    create_commitment,
    create_composite_proof,
    create_range_proof,
    create_set_membership_proof,
    create_threshold_proof,
    get_ai_compliance_template,
    get_ai_safety_template,
    get_manufacturing_qc_template,
    get_research_bounds_template,
    get_template,
    list_templates,
    verify_zkp_proof,
)


class TestBasicProofs:
    """Test basic ZKP proof creation"""

    def test_create_range_proof_satisfied(self):
        """Test range proof when value is in range"""
        proof = create_range_proof(
            claim_name="temperature",
            actual_value=0.5,
            min_value=0.0,
            max_value=1.0,
        )

        assert proof.proof_type == ZKPType.RANGE
        assert proof.claim_name == "temperature"
        assert proof.satisfied is True
        assert proof.commitment is not None
        assert len(proof.commitment) == 64  # SHA-256 hex
        assert "min_value" in proof.proof_data
        assert "max_value" in proof.proof_data
        assert proof.proof_data["min_value"] == 0.0
        assert proof.proof_data["max_value"] == 1.0

    def test_create_range_proof_unsatisfied(self):
        """Test range proof when value is out of range"""
        proof = create_range_proof(
            claim_name="temperature",
            actual_value=1.5,
            min_value=0.0,
            max_value=1.0,
        )

        assert proof.satisfied is False
        assert proof.commitment is not None

    def test_create_range_proof_boundary_inclusive(self):
        """Test range proof at boundaries (inclusive)"""
        # Lower boundary
        proof1 = create_range_proof(
            claim_name="value",
            actual_value=0.0,
            min_value=0.0,
            max_value=1.0,
            include_bounds=True,
        )
        assert proof1.satisfied is True

        # Upper boundary
        proof2 = create_range_proof(
            claim_name="value",
            actual_value=1.0,
            min_value=0.0,
            max_value=1.0,
            include_bounds=True,
        )
        assert proof2.satisfied is True

    def test_create_range_proof_boundary_exclusive(self):
        """Test range proof at boundaries (exclusive)"""
        # Lower boundary
        proof1 = create_range_proof(
            claim_name="value",
            actual_value=0.0,
            min_value=0.0,
            max_value=1.0,
            include_bounds=False,
        )
        assert proof1.satisfied is False

        # Upper boundary
        proof2 = create_range_proof(
            claim_name="value",
            actual_value=1.0,
            min_value=0.0,
            max_value=1.0,
            include_bounds=False,
        )
        assert proof2.satisfied is False

    def test_create_threshold_proof_lte_satisfied(self):
        """Test threshold proof with <= comparison (satisfied)"""
        proof = create_threshold_proof(
            claim_name="max_tokens",
            actual_value=2048,
            threshold=4096,
            comparison="lte",
        )

        assert proof.proof_type == ZKPType.THRESHOLD
        assert proof.satisfied is True
        assert proof.proof_data["threshold"] == 4096
        assert proof.proof_data["comparison"] == "lte"

    def test_create_threshold_proof_lte_unsatisfied(self):
        """Test threshold proof with <= comparison (unsatisfied)"""
        proof = create_threshold_proof(
            claim_name="max_tokens",
            actual_value=8192,
            threshold=4096,
            comparison="lte",
        )

        assert proof.satisfied is False

    def test_create_threshold_proof_gte_satisfied(self):
        """Test threshold proof with >= comparison (satisfied)"""
        proof = create_threshold_proof(
            claim_name="hardness",
            actual_value=60,
            threshold=55,
            comparison="gte",
        )

        assert proof.satisfied is True
        assert proof.proof_data["comparison"] == "gte"

    def test_create_threshold_proof_all_comparisons(self):
        """Test all threshold comparison operators"""
        comparisons = [
            ("lte", 2.0, 3.0, True),   # 2.0 <= 3.0
            ("lte", 3.0, 3.0, True),   # 3.0 <= 3.0
            ("lte", 4.0, 3.0, False),  # 4.0 <= 3.0
            ("gte", 4.0, 3.0, True),   # 4.0 >= 3.0
            ("gte", 3.0, 3.0, True),   # 3.0 >= 3.0
            ("gte", 2.0, 3.0, False),  # 2.0 >= 3.0
            ("lt", 2.0, 3.0, True),    # 2.0 < 3.0
            ("lt", 3.0, 3.0, False),   # 3.0 < 3.0
            ("gt", 4.0, 3.0, True),    # 4.0 > 3.0
            ("gt", 3.0, 3.0, False),   # 3.0 > 3.0
        ]

        for comp, value, threshold, expected_satisfied in comparisons:
            proof = create_threshold_proof(
                claim_name="test",
                actual_value=value,
                threshold=threshold,
                comparison=comp,
            )
            assert proof.satisfied == expected_satisfied, \
                f"Failed for {value} {comp} {threshold}"

    def test_create_threshold_proof_invalid_comparison(self):
        """Test threshold proof with invalid comparison"""
        with pytest.raises(ValueError, match="Invalid comparison"):
            create_threshold_proof(
                claim_name="test",
                actual_value=1.0,
                threshold=2.0,
                comparison="invalid",
            )

    def test_create_set_membership_proof_satisfied(self):
        """Test set membership proof when value is in set"""
        allowed_models = ["gpt-4", "claude-3", "gemini-pro"]
        proof = create_set_membership_proof(
            claim_name="model",
            actual_value="claude-3",
            allowed_set=allowed_models,
        )

        assert proof.proof_type == ZKPType.SET_MEMBERSHIP
        assert proof.satisfied is True
        assert proof.proof_data["allowed_set"] == allowed_models
        assert proof.proof_data["set_size"] == 3

    def test_create_set_membership_proof_unsatisfied(self):
        """Test set membership proof when value is not in set"""
        allowed_models = ["gpt-4", "claude-3", "gemini-pro"]
        proof = create_set_membership_proof(
            claim_name="model",
            actual_value="unknown-model",
            allowed_set=allowed_models,
        )

        assert proof.satisfied is False

    def test_create_composite_proof_and_all_satisfied(self):
        """Test composite proof with AND logic (all satisfied)"""
        proof1 = create_threshold_proof("temperature", 0.5, 1.0, "lte")
        proof2 = create_threshold_proof("max_tokens", 2048, 4096, "lte")

        composite = create_composite_proof([proof1, proof2], logic="and")

        assert composite.proof_type == ZKPType.COMPOSITE
        assert composite.satisfied is True
        assert composite.proof_data["logic"] == "and"
        assert composite.proof_data["count"] == 2

    def test_create_composite_proof_and_one_unsatisfied(self):
        """Test composite proof with AND logic (one unsatisfied)"""
        proof1 = create_threshold_proof("temperature", 0.5, 1.0, "lte")  # OK
        proof2 = create_threshold_proof("max_tokens", 8192, 4096, "lte")  # FAIL

        composite = create_composite_proof([proof1, proof2], logic="and")

        assert composite.satisfied is False

    def test_create_composite_proof_or_one_satisfied(self):
        """Test composite proof with OR logic (one satisfied)"""
        proof1 = create_threshold_proof("temperature", 0.5, 1.0, "lte")  # OK
        proof2 = create_threshold_proof("max_tokens", 8192, 4096, "lte")  # FAIL

        composite = create_composite_proof([proof1, proof2], logic="or")

        assert composite.satisfied is True

    def test_create_composite_proof_or_all_unsatisfied(self):
        """Test composite proof with OR logic (all unsatisfied)"""
        proof1 = create_threshold_proof("temperature", 1.5, 1.0, "lte")  # FAIL
        proof2 = create_threshold_proof("max_tokens", 8192, 4096, "lte")  # FAIL

        composite = create_composite_proof([proof1, proof2], logic="or")

        assert composite.satisfied is False

    def test_create_composite_proof_invalid_logic(self):
        """Test composite proof with invalid logic"""
        proof1 = create_threshold_proof("temperature", 0.5, 1.0, "lte")

        with pytest.raises(ValueError, match="Invalid logic"):
            create_composite_proof([proof1], logic="xor")


class TestCommitments:
    """Test cryptographic commitments"""

    def test_create_commitment_deterministic(self):
        """Test that same value + salt produces same commitment"""
        value = 0.7
        salt = "test_salt"

        commit1 = create_commitment(value, salt)
        commit2 = create_commitment(value, salt)

        assert commit1 == commit2

    def test_create_commitment_different_salt(self):
        """Test that different salts produce different commitments"""
        value = 0.7

        commit1 = create_commitment(value, "salt1")
        commit2 = create_commitment(value, "salt2")

        assert commit1 != commit2

    def test_create_commitment_different_value(self):
        """Test that different values produce different commitments"""
        salt = "test_salt"

        commit1 = create_commitment(0.7, salt)
        commit2 = create_commitment(0.8, salt)

        assert commit1 != commit2

    def test_create_commitment_complex_value(self):
        """Test commitment with complex data types"""
        values = [
            {"key": "value"},
            [1, 2, 3],
            "string",
            123,
            True,
        ]

        salt = "test_salt"
        for value in values:
            commitment = create_commitment(value, salt)
            assert len(commitment) == 64  # SHA-256 hex


class TestTemplates:
    """Test ZKP templates"""

    def test_get_ai_safety_template(self):
        """Test AI safety template"""
        template = get_ai_safety_template()

        assert template.template_type == TemplateType.AI_SAFETY
        assert template.name == "AI Safety Compliance"
        assert "temperature" in template.required_claims
        assert "max_tokens" in template.required_claims
        assert "model" in template.required_claims
        assert template.policy_id == "ai-safety-v1"

    def test_get_ai_compliance_template(self):
        """Test AI compliance template"""
        template = get_ai_compliance_template()

        assert template.template_type == TemplateType.AI_COMPLIANCE
        assert "temperature" in template.required_claims
        assert "prompt_length" in template.required_claims
        assert template.policy_id == "ai-compliance-fda-21-cfr-11"

    def test_get_manufacturing_qc_template(self):
        """Test manufacturing QC template"""
        template = get_manufacturing_qc_template()

        assert template.template_type == TemplateType.MANUFACTURING_QC
        assert "tolerance_mm" in template.required_claims
        assert "hardness_hrc" in template.required_claims
        assert "operator_certified" in template.required_claims
        assert template.policy_id == "manufacturing-qc-as9100d"

    def test_get_research_bounds_template(self):
        """Test research bounds template"""
        template = get_research_bounds_template()

        assert template.template_type == TemplateType.RESEARCH_BOUNDS
        assert "sample_size" in template.required_claims
        assert "p_value" in template.required_claims
        assert template.policy_id == "research-reproducibility-v1"

    def test_apply_ai_safety_template(self):
        """Test applying AI safety template"""
        template = get_ai_safety_template()

        claims = {
            "temperature": 0.7,
            "max_tokens": 4096,
            "model": "claude-sonnet-4.5",
        }

        proofs = apply_template(template, claims)

        assert len(proofs) == 3
        assert all(p.satisfied for p in proofs)
        assert all(p.metadata["template"] == "AI Safety Compliance" for p in proofs)

    def test_apply_ai_safety_template_violation(self):
        """Test applying AI safety template with violations"""
        template = get_ai_safety_template()

        claims = {
            "temperature": 1.5,  # Violation: > 1.0
            "max_tokens": 200000,  # Violation: > 100000
            "model": "unknown-model",  # Violation: not in approved list
        }

        proofs = apply_template(template, claims)

        assert len(proofs) == 3
        assert all(not p.satisfied for p in proofs)

    def test_apply_manufacturing_qc_template(self):
        """Test applying manufacturing QC template"""
        template = get_manufacturing_qc_template()

        claims = {
            "tolerance_mm": 0.005,  # Within ±0.01mm
            "hardness_hrc": 60,     # ≥ 55
            "operator_certified": True,
        }

        proofs = apply_template(template, claims)

        assert len(proofs) == 3
        assert all(p.satisfied for p in proofs)

    def test_apply_template_missing_claims(self):
        """Test applying template with missing claims"""
        template = get_ai_safety_template()

        claims = {
            "temperature": 0.7,
            # Missing: max_tokens, model
        }

        with pytest.raises(ValueError, match="Missing required claims"):
            apply_template(template, claims)

    def test_template_to_dict(self):
        """Test template serialization"""
        template = get_ai_safety_template()
        data = template.to_dict()

        assert data["template_type"] == "ai_safety"
        assert data["name"] == "AI Safety Compliance"
        assert "temperature" in data["required_claims"]
        assert "temperature" in data["proof_specs"]


class TestVerification:
    """Test ZKP proof verification"""

    def test_verify_zkp_proof_without_disclosure(self):
        """Test verification without value disclosure"""
        proof = create_range_proof("temperature", 0.7, 0.0, 1.0)

        result = verify_zkp_proof(proof)

        assert result["valid"] is True
        assert result["satisfied"] is True
        assert result["value_disclosed"] is False
        assert result["commitment_verified"] is None

    def test_verify_zkp_proof_with_disclosure(self):
        """Test verification with value disclosure"""
        proof = create_range_proof("temperature", 0.7, 0.0, 1.0)

        result = verify_zkp_proof(proof, disclosed_value=0.7)

        assert result["valid"] is True
        assert result["satisfied"] is True
        assert result["value_disclosed"] is True
        assert result["commitment_verified"] is True

    def test_verify_zkp_proof_wrong_disclosed_value(self):
        """Test verification with incorrect disclosed value"""
        proof = create_range_proof("temperature", 0.7, 0.0, 1.0)

        result = verify_zkp_proof(proof, disclosed_value=0.5)

        assert result["valid"] is False
        assert result["commitment_verified"] is False
        assert "Commitment verification failed" in result["errors"]

    def test_verify_zkp_proof_structure(self):
        """Test proof structure validation"""
        proof = create_range_proof("temperature", 0.7, 0.0, 1.0)
        proof.commitment = ""  # Invalid: empty commitment

        result = verify_zkp_proof(proof)

        assert result["valid"] is False
        assert "Missing commitment" in result["errors"]


class TestTemplateRegistry:
    """Test template registry functionality"""

    def test_get_template_by_name(self):
        """Test getting template by name"""
        template = get_template("ai_safety")

        assert template.template_type == TemplateType.AI_SAFETY
        assert template.name == "AI Safety Compliance"

    def test_get_template_invalid_name(self):
        """Test getting template with invalid name"""
        with pytest.raises(ValueError, match="Template 'invalid' not found"):
            get_template("invalid")

    def test_list_templates(self):
        """Test listing all templates"""
        templates = list_templates()

        assert len(templates) >= 4
        names = [t["name"] for t in templates]
        assert "ai_safety" in names
        assert "ai_compliance" in names
        assert "manufacturing_qc" in names
        assert "research_bounds" in names

        # Check structure
        for template_info in templates:
            assert "name" in template_info
            assert "type" in template_info
            assert "description" in template_info
            assert "required_claims" in template_info


class TestProofSerialization:
    """Test proof serialization"""

    def test_proof_to_dict(self):
        """Test proof serialization"""
        proof = create_range_proof("temperature", 0.7, 0.0, 1.0)

        data = proof.to_dict()

        assert data["proof_type"] == "range"
        assert data["claim_name"] == "temperature"
        assert "commitment" in data
        assert "proof_data" in data
        assert data["satisfied"] is True
        assert "timestamp" in data
        assert "nonce" in data

    def test_composite_proof_to_dict(self):
        """Test composite proof serialization"""
        proof1 = create_threshold_proof("temperature", 0.5, 1.0, "lte")
        proof2 = create_threshold_proof("max_tokens", 2048, 4096, "lte")
        composite = create_composite_proof([proof1, proof2], "and")

        data = composite.to_dict()

        assert data["proof_type"] == "composite"
        assert data["proof_data"]["logic"] == "and"
        assert data["proof_data"]["count"] == 2
        assert len(data["proof_data"]["proofs"]) == 2


class TestRealWorldScenarios:
    """Test real-world compliance scenarios"""

    def test_ai_temperature_compliance(self):
        """Test AI temperature compliance scenario"""
        # Scenario: Prove temperature ≤ 0.7 for regulatory compliance
        # without revealing exact value (which is proprietary)

        actual_temperature = 0.5  # Proprietary value
        regulatory_limit = 0.7

        proof = create_threshold_proof(
            claim_name="temperature",
            actual_value=actual_temperature,
            threshold=regulatory_limit,
            comparison="lte",
        )

        # Verifier can confirm compliance without knowing exact value
        assert proof.satisfied is True
        assert proof.proof_data["threshold"] == 0.7
        # actual_temperature is NOT in proof_data

        # Later, for audit, value can be disclosed
        result = verify_zkp_proof(proof, disclosed_value=0.5)
        assert result["commitment_verified"] is True

    def test_manufacturing_tolerance_compliance(self):
        """Test manufacturing tolerance compliance scenario"""
        # Scenario: Prove part is within tolerance without revealing
        # exact measurements (manufacturing IP)

        actual_tolerance = 0.005  # Proprietary measurement
        min_tolerance = -0.01
        max_tolerance = 0.01

        proof = create_range_proof(
            claim_name="tolerance_mm",
            actual_value=actual_tolerance,
            min_value=min_tolerance,
            max_value=max_tolerance,
        )

        # Customer can verify compliance without seeing exact measurement
        assert proof.satisfied is True
        assert proof.proof_data["min_value"] == -0.01
        assert proof.proof_data["max_value"] == 0.01

    def test_research_statistical_significance(self):
        """Test research statistical significance scenario"""
        # Scenario: Prove study meets statistical requirements
        # without revealing preliminary results

        template = get_research_bounds_template()

        claims = {
            "sample_size": 120,      # > 30 required
            "p_value": 0.03,         # < 0.05 required
            "methodology_approved": True,
        }

        proofs = apply_template(template, claims)

        # Journal can verify rigor without seeing results
        assert all(p.satisfied for p in proofs)
        assert len(proofs) == 3

    def test_ai_multi_constraint_compliance(self):
        """Test AI system with multiple compliance constraints"""
        # Scenario: AI system must satisfy multiple regulatory requirements
        # without revealing proprietary configuration

        template = get_ai_compliance_template()

        claims = {
            "temperature": 0.3,         # Within regulatory range
            "prompt_length": 15000,     # Under limit
            "human_review_required": True,
        }

        proofs = apply_template(template, claims)

        # All compliance requirements met
        assert all(p.satisfied for p in proofs)

        # Can create composite proof for overall compliance
        composite = create_composite_proof(proofs, logic="and")
        assert composite.satisfied is True


class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_zero_range(self):
        """Test range proof with min == max"""
        proof = create_range_proof("value", 5.0, 5.0, 5.0)
        assert proof.satisfied is True

    def test_negative_values(self):
        """Test with negative values"""
        proof = create_range_proof("value", -5.0, -10.0, 0.0)
        assert proof.satisfied is True

    def test_very_large_values(self):
        """Test with very large values"""
        proof = create_threshold_proof(
            "large_value",
            1e100,
            1e99,
            "gte",
        )
        assert proof.satisfied is True

    def test_empty_set_membership(self):
        """Test set membership with empty set"""
        proof = create_set_membership_proof(
            "value",
            "test",
            [],
        )
        assert proof.satisfied is False

    def test_single_element_set(self):
        """Test set membership with single element"""
        proof = create_set_membership_proof(
            "value",
            "test",
            ["test"],
        )
        assert proof.satisfied is True
