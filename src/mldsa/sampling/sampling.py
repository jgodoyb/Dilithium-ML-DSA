# src/mldsa/sampling/sampling.py
from mldsa.constants import Q

def coeff_from_three_bytes(b0: int, b1: int, b2: int):
    """
    Algoritmo 14: CoeffFromThreeBytes(b0, b1, b2).
    Genera un entero modulo q o None (símbolo de rechazo).
    """
    b2_prime = b2
    if b2 > 127:
        b2_prime = b2 - 128 # Ponemos el bit superior a cero.
        
    z = (2**16) * b2_prime + (2**8) * b1 + b0 # 0 <= z <= 2^23 - 1.
    
    if z < Q:
        return z
    return None

def coeff_from_half_byte(b: int, eta: int):
    """
    Algoritmo 15: CoeffFromHalfByte(b).
    Genera un coeficiente entre -eta y eta, o None.
    """
    if eta == 2 and b < 15:
        return 2 - (b % 5)
    elif eta == 4 and b < 9:
        return 4 - b
    return None