"""Signature generation functions."""

def sign_internal(sk: bytes, m: bytes, rnd: bytes) -> bytes:
    """Internal signature generation algorithm."""
    raise NotImplementedError

def sign(sk: bytes, m: bytes, ctx: bytes = b"") -> bytes:
    """ML-DSA signature generation."""
    raise NotImplementedError
