"""Signature verification functions."""

def verify_internal(pk: bytes, m: bytes, sig: bytes) -> bool:
    """Internal signature verification algorithm."""
    raise NotImplementedError

def verify(pk: bytes, m: bytes, sig: bytes, ctx: bytes = b"") -> bool:
    """ML-DSA signature verification."""
    raise NotImplementedError
