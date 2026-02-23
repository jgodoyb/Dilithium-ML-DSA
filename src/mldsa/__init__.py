
# src/mldsa/__init__.py
from .mldsa import (
    keygen,
    sign,
    verify,
    hash_sign,
    hash_verify
)

# Esto permite al usuario hacer simplemente:
# import mldsa
# pk, sk = mldsa.keygen()