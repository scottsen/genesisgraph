"""
GenesisGraph: Universal Verifiable Process Provenance

An open standard for proving how things were made.
"""

__version__ = "0.4.0"

from .validator import GenesisGraphValidator, validate
from .errors import (
    GenesisGraphError,
    ValidationError,
    SchemaError,
    HashError,
    SignatureError,
)
from .builder import (
    GenesisGraph,
    Entity,
    Operation,
    Tool,
    Attestation,
)

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
