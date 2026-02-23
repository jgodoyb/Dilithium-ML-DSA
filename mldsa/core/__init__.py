# src/mldsa/core/__init__.py

from .mldsa_internal import (
    keygen_internal,
    sign_internal,
    verify_internal
)

# Esto permite que cuando alguien haga:
# from mldsa.core import keygen_internal
# funcione perfectamente.