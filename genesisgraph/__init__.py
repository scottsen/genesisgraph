"""
GenesisGraph: Universal Verifiable Process Provenance

An open standard for proving how things were made.
"""

__version__ = "0.2.0"

from .validator import GenesisGraphValidator, validate
from .errors import (
    GenesisGraphError,
    ValidationError,
    SchemaError,
    HashError,
    SignatureError,
)

__all__ = [
    "GenesisGraphValidator",
    "validate",
    "GenesisGraphError",
    "ValidationError",
    "SchemaError",
    "HashError",
    "SignatureError",
]
