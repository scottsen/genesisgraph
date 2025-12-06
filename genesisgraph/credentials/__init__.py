"""
GenesisGraph Credentials Module

This module provides advanced cryptographic credential capabilities:
- SD-JWT (Selective Disclosure JWT) support per IETF draft-ietf-oauth-selective-disclosure-jwt
- Predicate disclosure for privacy-preserving claims (e.g., "temperature <= 0.3")
- BBS+ signature foundations for unlinkable presentations
- ZKP Templates for common compliance scenarios (AI safety, manufacturing QC, research)

These features enable enterprise IP protection and compliance requirements
by allowing verifiable claims without revealing underlying data.
"""

# Import predicates and ZKP templates (no external dependencies)
from .predicates import PredicateProof, PredicateType, create_predicate
from .zkp_templates import (
    TemplateType,
    ZKPProof,
    ZKPTemplate,
    ZKPType,
    apply_template,
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

# Optional imports (require additional dependencies)
try:
    from .sd_jwt import SDJWTError, SDJWTIssuer, SDJWTVerifier
    _SD_JWT_AVAILABLE = True
except ImportError:
    _SD_JWT_AVAILABLE = False
    SDJWTIssuer = None
    SDJWTVerifier = None
    SDJWTError = None

try:
    from .bbs_plus import BBSPlusIssuer, BBSPlusVerifier
    _BBS_PLUS_AVAILABLE = True
except ImportError:
    _BBS_PLUS_AVAILABLE = False
    BBSPlusIssuer = None
    BBSPlusVerifier = None

__all__ = [
    # Predicates (always available)
    "PredicateProof",
    "PredicateType",
    "create_predicate",
    # ZKP Templates (always available)
    "ZKPType",
    "ZKPProof",
    "ZKPTemplate",
    "TemplateType",
    "create_range_proof",
    "create_threshold_proof",
    "create_set_membership_proof",
    "create_composite_proof",
    "apply_template",
    "verify_zkp_proof",
    "get_template",
    "list_templates",
    "get_ai_safety_template",
    "get_ai_compliance_template",
    "get_manufacturing_qc_template",
    "get_research_bounds_template",
    # SD-JWT (optional)
    "SDJWTIssuer",
    "SDJWTVerifier",
    "SDJWTError",
    # BBS+ (optional)
    "BBSPlusIssuer",
    "BBSPlusVerifier",
]
