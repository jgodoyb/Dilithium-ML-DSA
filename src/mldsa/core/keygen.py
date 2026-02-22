"""Key generation functions."""

def keygen_internal(xi: bytes) -> tuple[bytes, bytes]:
    """Internal key generation algorithm."""
    raise NotImplementedError

def keygen() -> tuple[bytes, bytes]:
    """ML-DSA key generation."""
    raise NotImplementedError
