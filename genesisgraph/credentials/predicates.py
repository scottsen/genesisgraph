"""
Predicate Disclosure for Privacy-Preserving Claims

This module implements predicate-based selective disclosure, allowing
verification of claims without revealing exact values. For example:
- Prove "temperature <= 0.3" without revealing temperature=0.25
- Prove "age >= 18" without revealing age=25
- Prove "score in range [80, 100]" without revealing score=95

This is a practical implementation using cryptographic commitments.
For production zero-knowledge range proofs, consider Bulletproofs or zkSNARKs.
"""

import hashlib
import json
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass
import secrets


class PredicateType(Enum):
    """Types of predicates supported"""
    LESS_THAN = "lt"
    LESS_THAN_OR_EQUAL = "lte"
    GREATER_THAN = "gt"
    GREATER_THAN_OR_EQUAL = "gte"
    EQUAL = "eq"
    NOT_EQUAL = "neq"
    IN_RANGE = "in_range"
    IN_SET = "in_set"


@dataclass
class PredicateProof:
    """
    A predicate proof that demonstrates a claim satisfies a condition
    without revealing the exact value.

    Attributes:
        claim_name: Name of the claim (e.g., "temperature")
        predicate_type: Type of predicate (e.g., LESS_THAN_OR_EQUAL)
        threshold: Threshold value for comparison
        satisfied: Whether the predicate is satisfied
        commitment: Cryptographic commitment to the actual value
        salt: Random salt for commitment
        disclosed_value: Optional exact value (if full disclosure chosen)
    """
    claim_name: str
    predicate_type: PredicateType
    threshold: Any
    satisfied: bool
    commitment: str
    salt: str
    disclosed_value: Optional[Any] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "claim_name": self.claim_name,
            "predicate": self.predicate_type.value,
            "threshold": self.threshold,
            "satisfied": self.satisfied,
            "commitment": self.commitment,
            "disclosed": self.disclosed_value is not None,
            "value": self.disclosed_value if self.disclosed_value is not None else None,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PredicateProof":
        """Create from dictionary"""
        return cls(
            claim_name=data["claim_name"],
            predicate_type=PredicateType(data["predicate"]),
            threshold=data["threshold"],
            satisfied=data["satisfied"],
            commitment=data["commitment"],
            salt=data.get("salt", ""),
            disclosed_value=data.get("value"),
        )


def create_predicate(
    claim_name: str,
    actual_value: Any,
    predicate_type: Union[PredicateType, str],
    threshold: Any,
    disclose_value: bool = False,
) -> PredicateProof:
    """
    Create a predicate proof for a claim

    Args:
        claim_name: Name of the claim (e.g., "temperature")
        actual_value: The actual value to prove about
        predicate_type: Type of predicate (e.g., "lte" or PredicateType.LESS_THAN_OR_EQUAL)
        threshold: Threshold value for comparison
        disclose_value: If True, includes the actual value; if False, only commitment

    Returns:
        PredicateProof object

    Example:
        # Prove temperature <= 0.3 without revealing exact value
        proof = create_predicate("temperature", 0.25, "lte", 0.3, disclose_value=False)
        assert proof.satisfied == True
        assert proof.disclosed_value is None  # Value not disclosed
    """
    # Convert string to enum
    if isinstance(predicate_type, str):
        predicate_type = PredicateType(predicate_type)

    # Evaluate predicate
    satisfied = _evaluate_predicate(actual_value, predicate_type, threshold)

    # Create commitment to actual value
    salt = secrets.token_hex(16)
    commitment = _create_commitment(actual_value, salt)

    # Create proof
    proof = PredicateProof(
        claim_name=claim_name,
        predicate_type=predicate_type,
        threshold=threshold,
        satisfied=satisfied,
        commitment=commitment,
        salt=salt,
        disclosed_value=actual_value if disclose_value else None,
    )

    return proof


def verify_predicate(
    proof: PredicateProof,
    expected_claim_name: Optional[str] = None,
    verify_commitment: bool = True,
) -> Dict[str, Any]:
    """
    Verify a predicate proof

    Args:
        proof: The predicate proof to verify
        expected_claim_name: Expected claim name (optional)
        verify_commitment: Whether to verify commitment consistency

    Returns:
        Dict with verification results:
            - valid: Boolean indicating if proof is valid
            - satisfied: Whether predicate is satisfied
            - errors: List of validation errors
    """
    errors = []

    # Check claim name if specified
    if expected_claim_name and proof.claim_name != expected_claim_name:
        errors.append(f"Claim name mismatch: expected {expected_claim_name}, got {proof.claim_name}")

    # If value is disclosed, verify predicate
    if proof.disclosed_value is not None:
        actual_satisfied = _evaluate_predicate(
            proof.disclosed_value,
            proof.predicate_type,
            proof.threshold
        )
        if actual_satisfied != proof.satisfied:
            errors.append("Disclosed value does not satisfy claimed predicate")

        # Verify commitment
        if verify_commitment:
            expected_commitment = _create_commitment(proof.disclosed_value, proof.salt)
            if expected_commitment != proof.commitment:
                errors.append("Commitment verification failed")

    return {
        "valid": len(errors) == 0,
        "satisfied": proof.satisfied,
        "claim_name": proof.claim_name,
        "predicate": f"{proof.claim_name} {proof.predicate_type.value} {proof.threshold}",
        "errors": errors if errors else None,
    }


def create_range_proof(
    claim_name: str,
    actual_value: float,
    min_value: float,
    max_value: float,
    disclose_value: bool = False,
) -> PredicateProof:
    """
    Create a range proof showing value is in [min_value, max_value]

    This is a convenience wrapper around create_predicate for range proofs.

    Args:
        claim_name: Name of the claim
        actual_value: The actual value
        min_value: Minimum value of range (inclusive)
        max_value: Maximum value of range (inclusive)
        disclose_value: Whether to disclose the actual value

    Returns:
        PredicateProof for range containment

    Example:
        # Prove temperature is in [0.0, 0.3] without revealing exact value
        proof = create_range_proof("temperature", 0.25, 0.0, 0.3)
        assert proof.satisfied == True
    """
    satisfied = min_value <= actual_value <= max_value
    salt = secrets.token_hex(16)
    commitment = _create_commitment(actual_value, salt)

    proof = PredicateProof(
        claim_name=claim_name,
        predicate_type=PredicateType.IN_RANGE,
        threshold=(min_value, max_value),
        satisfied=satisfied,
        commitment=commitment,
        salt=salt,
        disclosed_value=actual_value if disclose_value else None,
    )

    return proof


def _evaluate_predicate(value: Any, predicate_type: PredicateType, threshold: Any) -> bool:
    """Evaluate a predicate"""
    if predicate_type == PredicateType.LESS_THAN:
        return value < threshold
    elif predicate_type == PredicateType.LESS_THAN_OR_EQUAL:
        return value <= threshold
    elif predicate_type == PredicateType.GREATER_THAN:
        return value > threshold
    elif predicate_type == PredicateType.GREATER_THAN_OR_EQUAL:
        return value >= threshold
    elif predicate_type == PredicateType.EQUAL:
        return value == threshold
    elif predicate_type == PredicateType.NOT_EQUAL:
        return value != threshold
    elif predicate_type == PredicateType.IN_RANGE:
        min_val, max_val = threshold
        return min_val <= value <= max_val
    elif predicate_type == PredicateType.IN_SET:
        return value in threshold
    else:
        raise ValueError(f"Unknown predicate type: {predicate_type}")


def _create_commitment(value: Any, salt: str) -> str:
    """
    Create a cryptographic commitment to a value

    Uses SHA-256 hash of (salt || value) to create a binding commitment.
    The salt prevents rainbow table attacks.
    """
    value_str = json.dumps(value, sort_keys=True)
    commitment_input = f"{salt}:{value_str}"
    commitment = hashlib.sha256(commitment_input.encode()).hexdigest()
    return commitment


def batch_create_predicates(
    claims: Dict[str, Any],
    predicates: Dict[str, Dict[str, Any]],
    disclose_values: Optional[List[str]] = None,
) -> List[PredicateProof]:
    """
    Create multiple predicate proofs in batch

    Args:
        claims: Dictionary of claim names to actual values
        predicates: Dictionary of claim names to predicate specifications
            Each spec should have: {"type": "lte", "threshold": 0.3}
        disclose_values: List of claim names to fully disclose (optional)

    Returns:
        List of PredicateProof objects

    Example:
        claims = {"temperature": 0.25, "prompt_length": 3500}
        predicates = {
            "temperature": {"type": "lte", "threshold": 0.3},
            "prompt_length": {"type": "lte", "threshold": 4000}
        }
        proofs = batch_create_predicates(claims, predicates)
    """
    disclose_values = disclose_values or []
    proofs = []

    for claim_name, predicate_spec in predicates.items():
        if claim_name not in claims:
            continue

        actual_value = claims[claim_name]
        predicate_type = predicate_spec["type"]
        threshold = predicate_spec["threshold"]
        disclose = claim_name in disclose_values

        proof = create_predicate(
            claim_name=claim_name,
            actual_value=actual_value,
            predicate_type=predicate_type,
            threshold=threshold,
            disclose_value=disclose,
        )
        proofs.append(proof)

    return proofs


def combine_with_sd_jwt(
    predicate_proofs: List[PredicateProof],
    sd_jwt_data: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Combine predicate proofs with SD-JWT for enhanced privacy

    This creates a credential that has:
    - SD-JWT for selective disclosure of standard claims
    - Predicate proofs for privacy-preserving threshold proofs

    Args:
        predicate_proofs: List of predicate proofs
        sd_jwt_data: SD-JWT data from SDJWTIssuer

    Returns:
        Combined credential with both SD-JWT and predicate proofs
    """
    return {
        "type": "GenesisGraphCredentialWithPredicates",
        "sd_jwt": sd_jwt_data,
        "predicate_proofs": [proof.to_dict() for proof in predicate_proofs],
        "version": "1.0",
    }
