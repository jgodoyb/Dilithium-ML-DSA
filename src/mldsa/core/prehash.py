"""HashML-DSA pre-hash wrapper."""

def hash_mldsa_sign(sk: bytes, m: bytes, ctx: bytes = b"", ph: str = "SHA-512") -> bytes:
    """HashML-DSA signature generation."""
    raise NotImplementedError

def hash_mldsa_verify(pk: bytes, m: bytes, sig: bytes, ctx: bytes = b"", ph: str = "SHA-512") -> bool:
    """HashML-DSA signature verification."""
    raise NotImplementedError
