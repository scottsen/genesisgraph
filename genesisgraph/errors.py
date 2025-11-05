"""GenesisGraph error types"""


class GenesisGraphError(Exception):
    """Base exception for all GenesisGraph errors"""
    pass


class ValidationError(GenesisGraphError):
    """Raised when validation fails"""
    pass


class SchemaError(ValidationError):
    """Raised when schema validation fails"""
    pass


class HashError(ValidationError):
    """Raised when hash verification fails"""
    pass


class SignatureError(ValidationError):
    """Raised when signature verification fails"""
    pass
