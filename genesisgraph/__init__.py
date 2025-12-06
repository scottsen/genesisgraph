"""
GenesisGraph: Universal Verifiable Process Provenance

An open standard for proving how things were made.
"""

__version__ = "0.3.0"

from .builder import (
    Attestation,
    Entity,
    GenesisGraph,
    Operation,
    Tool,
)
from .errors import (
    GenesisGraphError,
    HashError,
    SchemaError,
    SignatureError,
    ValidationError,
)
from .validator import GenesisGraphValidator, validate

__all__ = [
    # Validator
    "GenesisGraphValidator",
    "validate",
    # Errors
    "GenesisGraphError",
    "ValidationError",
    "SchemaError",
    "HashError",
    "SignatureError",
    # Builder API
    "GenesisGraph",
    "Entity",
    "Operation",
    "Tool",
    "Attestation",
]
