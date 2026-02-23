"""Custom type hints for ML-DSA."""
from typing import TypeAlias

Polynomial: TypeAlias = list[int]
PolynomialVector: TypeAlias = list[Polynomial]
PolynomialMatrix: TypeAlias = list[PolynomialVector]
