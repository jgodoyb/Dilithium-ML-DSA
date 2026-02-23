# src/mldsa/sampling/expanders.py
from mldsa.primitives.conversions import integer_to_bytes
from mldsa.sampling.samplers import rej_ntt_poly, rej_bounded_poly

def expand_a(rho: bytes, k: int, l: int) -> list:
    """
    Algoritmo 32: ExpandA(rho)
    Genera una matriz A de tamaño k x l con polinomios en T_q.
    """
    # Inicializamos una matriz (k filas, l columnas)
    A_hat = [[None for _ in range(l)] for _ in range(k)]
    
    for r in range(k):
        for s in range(l):
            # rho' = rho || IntegerToBytes(s, 1) || IntegerToBytes(r, 1)
            rho_prime = rho + integer_to_bytes(s, 1) + integer_to_bytes(r, 1)
            
            # Generamos el polinomio para esta celda de la matriz
            A_hat[r][s] = rej_ntt_poly(rho_prime)
            
    return A_hat

def expand_s(rho_prime: bytes, k: int, l: int, eta: int) -> tuple:
    """
    Algoritmo 33: ExpandS(rho')
    Genera los vectores secretos s1 (longitud l) y s2 (longitud k) 
    con coeficientes en el rango [-eta, eta].
    """
    s1 = [None] * l
    s2 = [None] * k
    
    # Generamos s1
    for r in range(l):
        # semilla = rho' || IntegerToBytes(r, 2)
        seed = rho_prime + integer_to_bytes(r, 2)
        s1[r] = rej_bounded_poly(seed, eta)
        
    # Generamos s2
    for r in range(k):
        # semilla = rho' || IntegerToBytes(r + l, 2)
        seed = rho_prime + integer_to_bytes(r + l, 2)
        s2[r] = rej_bounded_poly(seed, eta)
        
    return s1, s2