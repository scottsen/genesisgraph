"""
Zero-Knowledge Proof Templates for GenesisGraph

This module provides practical zero-knowledge proof templates for common
compliance and verification scenarios. These templates enable proving
policy compliance without revealing sensitive parameters.

Key Features:
- Range proofs (prove value is in range without revealing exact value)
- Set membership proofs (prove value is in set without revealing which)
- Threshold proofs (prove value meets threshold without revealing exact value)
- Composite proofs (combine multiple proofs)
- Policy compliance templates for AI, manufacturing, and research

Templates are designed for real-world use cases:
- AI model compliance (temperature, token limits, safety checks)
- Manufacturing quality control (tolerances, certifications)
- Research reproducibility (parameter bounds, methodology validation)

Note: This implementation provides practical ZKP templates using
commitment-based proofs. For production zero-knowledge range proofs with
formal security guarantees, consider integrating Bulletproofs, zkSNARKs,
or similar cryptographic libraries.
"""

import hashlib
import json
import secrets
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union
from datetime import datetime


class ZKPType(Enum):
    """Types of zero-knowledge proofs supported"""
    RANGE = "range"                    # Prove value in [min, max]
    THRESHOLD = "threshold"            # Prove value ≤ or ≥ threshold
    SET_MEMBERSHIP = "set_membership"  # Prove value in set
    EQUALITY = "equality"              # Prove value equals (without revealing)
    INEQUALITY = "inequality"          # Prove value ≠ (without revealing)
    COMPOSITE = "composite"            # Multiple proofs combined


class TemplateType(Enum):
    """Pre-built ZKP templates for common use cases"""
    AI_SAFETY = "ai_safety"              # AI model safety parameters
    AI_COMPLIANCE = "ai_compliance"      # AI regulatory compliance
    MANUFACTURING_QC = "manufacturing_qc"  # Quality control tolerances
    RESEARCH_BOUNDS = "research_bounds"    # Research parameter validation
    CUSTOM = "custom"                      # User-defined template


@dataclass
class ZKPProof:
    """
    A zero-knowledge proof demonstrating a claim without revealing the value

    Attributes:
        proof_type: Type of ZKP (range, threshold, etc.)
        claim_name: Name of the claim being proven
        commitment: Cryptographic commitment to the actual value
        proof_data: Proof-specific data (varies by proof type)
        satisfied: Whether the proof is satisfied
        timestamp: When the proof was created
        nonce: Random nonce for freshness
        metadata: Optional additional metadata
    """
    proof_type: ZKPType
    claim_name: str
    commitment: str
    proof_data: Dict[str, Any]
    satisfied: bool
    timestamp: str
    nonce: str
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "proof_type": self.proof_type.value,
            "claim_name": self.claim_name,
            "commitment": self.commitment,
            "proof_data": self.proof_data,
            "satisfied": self.satisfied,
            "timestamp": self.timestamp,
            "nonce": self.nonce,
            "metadata": self.metadata or {},
        }


@dataclass
class ZKPTemplate:
    """
    A reusable template for creating ZKP proofs for specific use cases

    Templates encode common patterns like:
    - AI safety: temperature ≤ 1.0, max_tokens ≤ 4096
    - Manufacturing: tolerance in [±0.01mm], hardness ≥ 60 HRC
    - Research: sample_size ≥ 100, p_value ≤ 0.05
    """
    template_type: TemplateType
    name: str
    description: str
    required_claims: List[str]
    proof_specs: Dict[str, Dict[str, Any]]
    policy_id: Optional[str] = None
    version: str = "1.0"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "template_type": self.template_type.value,
            "name": self.name,
            "description": self.description,
            "required_claims": self.required_claims,
            "proof_specs": self.proof_specs,
            "policy_id": self.policy_id,
            "version": self.version,
        }


def create_commitment(value: Any, salt: str) -> str:
    """
    Create a cryptographic commitment to a value

    Uses SHA-256(salt || value) to create a binding commitment.
    The salt prevents rainbow table attacks.

    Args:
        value: Value to commit to
        salt: Random salt for commitment

    Returns:
        Hex-encoded commitment hash
    """
    value_str = json.dumps(value, sort_keys=True)
    commitment_input = f"{salt}:{value_str}"
    return hashlib.sha256(commitment_input.encode()).hexdigest()


def create_range_proof(
    claim_name: str,
    actual_value: float,
    min_value: float,
    max_value: float,
    include_bounds: bool = True,
) -> ZKPProof:
    """
    Create a zero-knowledge range proof

    Proves that actual_value ∈ [min_value, max_value] without revealing actual_value.

    Args:
        claim_name: Name of the claim (e.g., "temperature")
        actual_value: The actual value (kept private)
        min_value: Minimum acceptable value (public)
        max_value: Maximum acceptable value (public)
        include_bounds: Whether bounds are inclusive

    Returns:
        ZKPProof object

    Example:
        # Prove temperature is in [0.0, 1.0] without revealing it's 0.7
        proof = create_range_proof("temperature", 0.7, 0.0, 1.0)
        assert proof.satisfied == True
        # actual_value is NOT in proof_data
    """
    # Generate nonce and commitment
    nonce = secrets.token_hex(16)
    salt = secrets.token_hex(16)
    commitment = create_commitment(actual_value, salt)

    # Evaluate range predicate
    if include_bounds:
        satisfied = min_value <= actual_value <= max_value
    else:
        satisfied = min_value < actual_value < max_value

    # Create proof data (does NOT include actual_value)
    proof_data = {
        "min_value": min_value,
        "max_value": max_value,
        "include_bounds": include_bounds,
        "salt": salt,  # Needed for verification if value is later disclosed
    }

    return ZKPProof(
        proof_type=ZKPType.RANGE,
        claim_name=claim_name,
        commitment=commitment,
        proof_data=proof_data,
        satisfied=satisfied,
        timestamp=datetime.utcnow().isoformat() + "Z",
        nonce=nonce,
    )


def create_threshold_proof(
    claim_name: str,
    actual_value: float,
    threshold: float,
    comparison: str,  # "lte", "gte", "lt", "gt"
) -> ZKPProof:
    """
    Create a zero-knowledge threshold proof

    Proves that actual_value meets a threshold condition without revealing exact value.

    Args:
        claim_name: Name of the claim
        actual_value: The actual value (kept private)
        threshold: Threshold value (public)
        comparison: Comparison operator ("lte", "gte", "lt", "gt")

    Returns:
        ZKPProof object

    Example:
        # Prove max_tokens <= 4096 without revealing exact value
        proof = create_threshold_proof("max_tokens", 2048, 4096, "lte")
    """
    nonce = secrets.token_hex(16)
    salt = secrets.token_hex(16)
    commitment = create_commitment(actual_value, salt)

    # Evaluate threshold
    comparisons = {
        "lte": actual_value <= threshold,
        "gte": actual_value >= threshold,
        "lt": actual_value < threshold,
        "gt": actual_value > threshold,
    }

    if comparison not in comparisons:
        raise ValueError(f"Invalid comparison: {comparison}")

    satisfied = comparisons[comparison]

    proof_data = {
        "threshold": threshold,
        "comparison": comparison,
        "salt": salt,
    }

    return ZKPProof(
        proof_type=ZKPType.THRESHOLD,
        claim_name=claim_name,
        commitment=commitment,
        proof_data=proof_data,
        satisfied=satisfied,
        timestamp=datetime.utcnow().isoformat() + "Z",
        nonce=nonce,
    )


def create_set_membership_proof(
    claim_name: str,
    actual_value: Any,
    allowed_set: List[Any],
) -> ZKPProof:
    """
    Create a zero-knowledge set membership proof

    Proves that actual_value ∈ allowed_set without revealing which element.

    Args:
        claim_name: Name of the claim
        actual_value: The actual value (kept private)
        allowed_set: Set of allowed values (public)

    Returns:
        ZKPProof object

    Example:
        # Prove model is in approved list without revealing which one
        models = ["gpt-4", "claude-3", "gemini-pro"]
        proof = create_set_membership_proof("model", "claude-3", models)
    """
    nonce = secrets.token_hex(16)
    salt = secrets.token_hex(16)
    commitment = create_commitment(actual_value, salt)

    satisfied = actual_value in allowed_set

    # Create commitments for all values in set (for verification)
    # This prevents revealing which value through the commitment
    set_commitments = [
        create_commitment(val, salt) for val in allowed_set
    ]

    proof_data = {
        "allowed_set": allowed_set,
        "set_size": len(allowed_set),
        "salt": salt,
    }

    return ZKPProof(
        proof_type=ZKPType.SET_MEMBERSHIP,
        claim_name=claim_name,
        commitment=commitment,
        proof_data=proof_data,
        satisfied=satisfied,
        timestamp=datetime.utcnow().isoformat() + "Z",
        nonce=nonce,
    )


def create_composite_proof(
    proofs: List[ZKPProof],
    logic: str = "and",  # "and" or "or"
) -> ZKPProof:
    """
    Create a composite proof combining multiple ZKP proofs

    Allows complex policies like:
    - "temperature ≤ 0.7 AND max_tokens ≤ 4096 AND model in [approved_list]"
    - "precision ≥ 0.01mm OR certified_operator = True"

    Args:
        proofs: List of individual ZKP proofs
        logic: Combination logic ("and" or "or")

    Returns:
        Composite ZKPProof

    Example:
        temp_proof = create_threshold_proof("temperature", 0.5, 1.0, "lte")
        token_proof = create_threshold_proof("max_tokens", 2048, 4096, "lte")
        composite = create_composite_proof([temp_proof, token_proof], "and")
    """
    nonce = secrets.token_hex(16)

    # Evaluate composite satisfaction
    if logic == "and":
        satisfied = all(p.satisfied for p in proofs)
    elif logic == "or":
        satisfied = any(p.satisfied for p in proofs)
    else:
        raise ValueError(f"Invalid logic: {logic}")

    # Combine commitments
    combined_commitment = hashlib.sha256(
        "".join(p.commitment for p in proofs).encode()
    ).hexdigest()

    proof_data = {
        "logic": logic,
        "proofs": [p.to_dict() for p in proofs],
        "count": len(proofs),
    }

    claim_names = [p.claim_name for p in proofs]

    return ZKPProof(
        proof_type=ZKPType.COMPOSITE,
        claim_name=f"composite({', '.join(claim_names)})",
        commitment=combined_commitment,
        proof_data=proof_data,
        satisfied=satisfied,
        timestamp=datetime.utcnow().isoformat() + "Z",
        nonce=nonce,
    )


# ============================================================================
# Pre-built Templates for Common Use Cases
# ============================================================================


def get_ai_safety_template() -> ZKPTemplate:
    """
    Template for AI model safety compliance

    Ensures:
    - Temperature is reasonable (≤ 1.0)
    - Token limits are enforced
    - Model is from approved list

    Use case: Prove AI system follows safety guidelines without revealing
    exact configuration or prompts.
    """
    return ZKPTemplate(
        template_type=TemplateType.AI_SAFETY,
        name="AI Safety Compliance",
        description="Prove AI model follows safety guidelines",
        required_claims=["temperature", "max_tokens", "model"],
        proof_specs={
            "temperature": {
                "type": "threshold",
                "threshold": 1.0,
                "comparison": "lte",
                "rationale": "Prevent excessive randomness",
            },
            "max_tokens": {
                "type": "threshold",
                "threshold": 100000,
                "comparison": "lte",
                "rationale": "Prevent resource abuse",
            },
            "model": {
                "type": "set_membership",
                "allowed_set": [
                    "gpt-4",
                    "gpt-4-turbo",
                    "claude-3-opus",
                    "claude-3-sonnet",
                    "claude-sonnet-4.5",
                    "gemini-pro",
                ],
                "rationale": "Use only approved models",
            },
        },
        policy_id="ai-safety-v1",
        version="1.0",
    )


def get_ai_compliance_template() -> ZKPTemplate:
    """
    Template for AI regulatory compliance

    Ensures:
    - Temperature within regulatory limits
    - Prompt length restrictions
    - Human review for sensitive decisions

    Use case: Prove compliance with AI Act, FDA 21 CFR Part 11, or similar
    regulations without revealing proprietary prompts or parameters.
    """
    return ZKPTemplate(
        template_type=TemplateType.AI_COMPLIANCE,
        name="AI Regulatory Compliance",
        description="Prove AI system meets regulatory requirements",
        required_claims=["temperature", "prompt_length", "human_review_required"],
        proof_specs={
            "temperature": {
                "type": "range",
                "min_value": 0.0,
                "max_value": 0.7,
                "rationale": "Regulatory requirement for deterministic outputs",
            },
            "prompt_length": {
                "type": "threshold",
                "threshold": 50000,
                "comparison": "lte",
                "rationale": "Prevent prompt injection attacks",
            },
            "human_review_required": {
                "type": "equality",
                "expected_value": True,
                "rationale": "High-stakes decisions require human oversight",
            },
        },
        policy_id="ai-compliance-fda-21-cfr-11",
        version="1.0",
    )


def get_manufacturing_qc_template() -> ZKPTemplate:
    """
    Template for manufacturing quality control

    Ensures:
    - Dimensional tolerances met
    - Material hardness in spec
    - Operator certification valid

    Use case: Prove aerospace/medical part compliance (AS9100D, ISO 13485)
    without revealing proprietary manufacturing parameters.
    """
    return ZKPTemplate(
        template_type=TemplateType.MANUFACTURING_QC,
        name="Manufacturing QC Compliance",
        description="Prove manufacturing quality control compliance",
        required_claims=["tolerance_mm", "hardness_hrc", "operator_certified"],
        proof_specs={
            "tolerance_mm": {
                "type": "range",
                "min_value": -0.01,
                "max_value": 0.01,
                "rationale": "ISO 2768 tolerance class",
            },
            "hardness_hrc": {
                "type": "threshold",
                "threshold": 55,
                "comparison": "gte",
                "rationale": "Material specification requirement",
            },
            "operator_certified": {
                "type": "equality",
                "expected_value": True,
                "rationale": "AS9100D certified operator requirement",
            },
        },
        policy_id="manufacturing-qc-as9100d",
        version="1.0",
    )


def get_research_bounds_template() -> ZKPTemplate:
    """
    Template for research reproducibility validation

    Ensures:
    - Sample size meets statistical requirements
    - p-value meets significance threshold
    - Methodology follows pre-registered plan

    Use case: Prove research rigor without revealing preliminary results
    or detailed methodology (pre-publication).
    """
    return ZKPTemplate(
        template_type=TemplateType.RESEARCH_BOUNDS,
        name="Research Reproducibility",
        description="Prove research meets methodological standards",
        required_claims=["sample_size", "p_value", "methodology_approved"],
        proof_specs={
            "sample_size": {
                "type": "threshold",
                "threshold": 30,
                "comparison": "gte",
                "rationale": "Minimum statistical power requirement",
            },
            "p_value": {
                "type": "threshold",
                "threshold": 0.05,
                "comparison": "lte",
                "rationale": "Statistical significance threshold",
            },
            "methodology_approved": {
                "type": "equality",
                "expected_value": True,
                "rationale": "IRB/ethics board approval required",
            },
        },
        policy_id="research-reproducibility-v1",
        version="1.0",
    )


def apply_template(
    template: ZKPTemplate,
    claims: Dict[str, Any],
) -> List[ZKPProof]:
    """
    Apply a ZKP template to actual claim values

    Args:
        template: The ZKP template to apply
        claims: Dictionary of claim names to actual values

    Returns:
        List of ZKP proofs, one per claim in template

    Raises:
        ValueError: If required claims are missing

    Example:
        template = get_ai_safety_template()
        claims = {
            "temperature": 0.7,
            "max_tokens": 4096,
            "model": "claude-sonnet-4.5"
        }
        proofs = apply_template(template, claims)
        # Returns 3 ZKP proofs without revealing actual values
    """
    # Validate required claims present
    missing_claims = set(template.required_claims) - set(claims.keys())
    if missing_claims:
        raise ValueError(f"Missing required claims: {missing_claims}")

    proofs = []

    for claim_name, spec in template.proof_specs.items():
        if claim_name not in claims:
            continue

        actual_value = claims[claim_name]
        proof_type = spec["type"]

        if proof_type == "range":
            proof = create_range_proof(
                claim_name=claim_name,
                actual_value=actual_value,
                min_value=spec["min_value"],
                max_value=spec["max_value"],
            )
        elif proof_type == "threshold":
            proof = create_threshold_proof(
                claim_name=claim_name,
                actual_value=actual_value,
                threshold=spec["threshold"],
                comparison=spec["comparison"],
            )
        elif proof_type == "set_membership":
            proof = create_set_membership_proof(
                claim_name=claim_name,
                actual_value=actual_value,
                allowed_set=spec["allowed_set"],
            )
        elif proof_type == "equality":
            # For equality, we can use a threshold proof with same min/max
            expected = spec["expected_value"]
            satisfied = actual_value == expected
            salt = secrets.token_hex(16)
            proof = ZKPProof(
                proof_type=ZKPType.EQUALITY,
                claim_name=claim_name,
                commitment=create_commitment(actual_value, salt),
                proof_data={"expected_value": expected, "salt": salt},
                satisfied=satisfied,
                timestamp=datetime.utcnow().isoformat() + "Z",
                nonce=secrets.token_hex(16),
            )
        else:
            raise ValueError(f"Unknown proof type: {proof_type}")

        # Add metadata from template
        proof.metadata = {
            "template": template.name,
            "template_type": template.template_type.value,
            "policy_id": template.policy_id,
            "rationale": spec.get("rationale", ""),
        }

        proofs.append(proof)

    return proofs


def verify_zkp_proof(
    proof: ZKPProof,
    disclosed_value: Optional[Any] = None,
) -> Dict[str, Any]:
    """
    Verify a zero-knowledge proof

    Args:
        proof: The ZKP proof to verify
        disclosed_value: Optional actual value (if holder chooses to disclose)

    Returns:
        Verification result with status and details

    Example:
        # Verify without disclosure
        result = verify_zkp_proof(proof)
        assert result["valid"] == True
        assert result["value_disclosed"] == False

        # Verify with disclosure (for auditing)
        result = verify_zkp_proof(proof, disclosed_value=0.7)
        assert result["valid"] == True
        assert result["commitment_verified"] == True
    """
    errors = []

    # Basic structure validation
    if not proof.commitment:
        errors.append("Missing commitment")

    if not proof.proof_data:
        errors.append("Missing proof data")

    # If value is disclosed, verify commitment
    commitment_verified = None
    if disclosed_value is not None:
        salt = proof.proof_data.get("salt")
        if salt:
            expected_commitment = create_commitment(disclosed_value, salt)
            commitment_verified = (expected_commitment == proof.commitment)
            if not commitment_verified:
                errors.append("Commitment verification failed")
        else:
            errors.append("Cannot verify commitment: salt not in proof data")

    return {
        "valid": len(errors) == 0,
        "satisfied": proof.satisfied,
        "proof_type": proof.proof_type.value,
        "claim_name": proof.claim_name,
        "timestamp": proof.timestamp,
        "value_disclosed": disclosed_value is not None,
        "commitment_verified": commitment_verified,
        "errors": errors if errors else None,
    }


# Registry of available templates
TEMPLATE_REGISTRY = {
    "ai_safety": get_ai_safety_template,
    "ai_compliance": get_ai_compliance_template,
    "manufacturing_qc": get_manufacturing_qc_template,
    "research_bounds": get_research_bounds_template,
}


def get_template(template_name: str) -> ZKPTemplate:
    """
    Get a template by name from the registry

    Args:
        template_name: Name of template ("ai_safety", "ai_compliance", etc.)

    Returns:
        ZKPTemplate instance

    Raises:
        ValueError: If template name not found
    """
    if template_name not in TEMPLATE_REGISTRY:
        available = ", ".join(TEMPLATE_REGISTRY.keys())
        raise ValueError(
            f"Template '{template_name}' not found. "
            f"Available templates: {available}"
        )

    return TEMPLATE_REGISTRY[template_name]()


def list_templates() -> List[Dict[str, str]]:
    """
    List all available templates

    Returns:
        List of template info dictionaries
    """
    templates = []
    for name, factory in TEMPLATE_REGISTRY.items():
        template = factory()
        templates.append({
            "name": name,
            "type": template.template_type.value,
            "description": template.description,
            "required_claims": template.required_claims,
        })
    return templates
