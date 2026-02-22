"""Parameters for ML-DSA-44."""
from dataclasses import dataclass

@dataclass
class MLDSA44Params:
    """ML-DSA-44 parameter set."""
    k: int = 0
    l: int = 0
    eta: int = 0
    tau: int = 0
    beta: int = 0
    omega: int = 0
