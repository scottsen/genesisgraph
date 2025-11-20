"""
GenesisGraph Credentials Module

This module provides advanced cryptographic credential capabilities:
- SD-JWT (Selective Disclosure JWT) support per IETF draft-ietf-oauth-selective-disclosure-jwt
- Predicate disclosure for privacy-preserving claims (e.g., "temperature <= 0.3")
- BBS+ signature foundations for unlinkable presentations

These features enable enterprise IP protection and compliance requirements
by allowing verifiable claims without revealing underlying data.
"""

from .sd_jwt import SDJWTIssuer, SDJWTVerifier, SDJWTError
from .predicates import PredicateProof, PredicateType, create_predicate
from .bbs_plus import BBSPlusIssuer, BBSPlusVerifier

__all__ = [
    "SDJWTIssuer",
    "SDJWTVerifier",
    "SDJWTError",
    "PredicateProof",
    "PredicateType",
    "create_predicate",
    "BBSPlusIssuer",
    "BBSPlusVerifier",
]
