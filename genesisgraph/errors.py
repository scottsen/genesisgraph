"""GenesisGraph error types"""


class GenesisGraphError(Exception):
    """Base exception for all GenesisGraph errors"""


class ValidationError(GenesisGraphError):
    """Raised when validation fails"""


class SchemaError(ValidationError):
    """Raised when schema validation fails"""


class HashError(ValidationError):
    """Raised when hash verification fails"""


class SignatureError(ValidationError):
    """Raised when signature verification fails"""
