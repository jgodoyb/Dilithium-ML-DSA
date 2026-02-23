"""Custom exceptions for ML-DSA."""

class MLDSAError(Exception):
    """Base class for ML-DSA exceptions."""
    pass

class VerificationError(MLDSAError):
    """Exception raised when signature verification fails."""
    pass
