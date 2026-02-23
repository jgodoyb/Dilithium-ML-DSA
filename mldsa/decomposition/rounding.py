# src/mldsa/decomposition/rounding.py
from mldsa.constants import Q, D

def mod_centered(r: int, alpha: int) -> int:
    """
    Calcula r mod+- alpha. 
    Devuelve un valor en el rango (-alpha/2, alpha/2].
    """
    r_mod = r % alpha
    if r_mod > alpha // 2:
        r_mod -= alpha
    return r_mod

def power2round(r, d: int = D):
    """
    Algoritmo 35: Power2Round(r)
    Descompone r en (r1, r0) tal que r = r1*2^d + r0 mod q.
    Soporta enteros o listas de enteros (polinomios).
    """
    # Si r es una lista, aplicamos la función a cada elemento recursivamente
    if isinstance(r, list):
        r1_list = [0] * len(r)
        r0_list = [0] * len(r)
        for i in range(len(r)):
            r1_list[i], r0_list[i] = power2round(r[i], d)
        return r1_list, r0_list

    # Lógica para un escalar
    r_plus = r % Q
    r0 = mod_centered(r_plus, 2**d)
    r1 = (r_plus - r0) // (2**d)
    return r1, r0

def decompose(r, gamma2: int):
    """
    Algoritmo 36: Decompose(r)
    Descompone r en (r1, r0) tal que r = r1*(2*gamma2) + r0 mod q.
    """
    if isinstance(r, list):
        r1_list = [0] * len(r)
        r0_list = [0] * len(r)
        for i in range(len(r)):
            r1_list[i], r0_list[i] = decompose(r[i], gamma2)
        return r1_list, r0_list

    alpha = 2 * gamma2
    r_plus = r % Q
    r0 = mod_centered(r_plus, alpha)
    
    if (r_plus - r0) == (Q - 1):
        r1 = 0
        r0 = r0 - 1
    else:
        r1 = (r_plus - r0) // alpha
        
    return r1, r0

def highbits(r, gamma2: int):
    """
    Algoritmo 37: HighBits(r)
    Devuelve r1 de Decompose(r).
    """
    r1, _ = decompose(r, gamma2)
    return r1

def lowbits(r, gamma2: int):
    """
    Algoritmo 38: LowBits(r)
    Devuelve r0 de Decompose(r).
    """
    _, r0 = decompose(r, gamma2)
    return r0

def make_hint(z, r, gamma2: int):
    """
    Algoritmo 39: MakeHint(z, r)
    Calcula un bit (0 o 1) indicando si sumar z a r altera los bits altos de r.
    """
    if isinstance(z, list) and isinstance(r, list):
        return [make_hint(z[i], r[i], gamma2) for i in range(len(z))]

    r1 = highbits(r, gamma2)
    v1 = highbits(r + z, gamma2)
    return 1 if r1 != v1 else 0

def use_hint(h, r, gamma2: int):
    """
    Algoritmo 40: UseHint(h, r)
    Devuelve los bits altos de r ajustados según la pista (hint) h.
    """
    if isinstance(h, list) and isinstance(r, list):
        return [use_hint(h[i], r[i], gamma2) for i in range(len(h))]

    m = (Q - 1) // (2 * gamma2)
    r1, r0 = decompose(r, gamma2)
    
    if h == 1 and r0 > 0:
        return (r1 + 1) % m
    if h == 1 and r0 <= 0:
        return (r1 - 1) % m
    return r1