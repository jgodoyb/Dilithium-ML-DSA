# src/mldsa/ntt/ntt.py
from mldsa.constants import Q
from mldsa.primitives.conversions import bit_rev_8

# --- GENERACIÓN DE LA TABLA DE ZETAS ---
# FIPS 204 define la raíz de unidad zeta = 1753
ZETA = 1753
# Precalculamos el array zetas: zetas[m] = zeta^(BitRev8(m)) mod q
ZETAS = [pow(ZETA, bit_rev_8(m), Q) for m in range(256)]

def ntt(w: list) -> list:
    """
    Algoritmo 41: NTT(w)
    Transformada de Números. Transforma un polinomio de R_q a T_q.
    """
    # 1-3: Copiamos el polinomio para no mutar el original
    w_hat = w.copy()
    
    m = 0
    length = 128
    
    # 6: while len >= 1
    while length >= 1:
        start = 0
        # 8: while start < 256
        while start < 256:
            m = m + 1
            z = ZETAS[m] # zeta^BitRev8(m) mod q
            
            # 11: for j from start to start + len - 1
            for j in range(start, start + length):
                # La operación "Butterfly" (Mariposa)
                t = (z * w_hat[j + length]) % Q
                w_hat[j + length] = (w_hat[j] - t) % Q
                w_hat[j] = (w_hat[j] + t) % Q
                
            start = start + 2 * length
        length = length // 2
        
    return w_hat

def ntt_inv(w_hat: list) -> list:
    """
    Algoritmo 42: NTT^-1(w_hat)
    Transformada Inversa. Transforma un polinomio de T_q a R_q.
    """
    w = w_hat.copy()
    m = 256
    length = 1
    
    # 6: while len < 256
    while length < 256:
        start = 0
        while start < 256:
            m = m - 1
            # 10: z <- -zetas[m] mod q
            z = (-ZETAS[m]) % Q
            
            for j in range(start, start + length):
                t = w[j]
                w[j] = (t + w[j + length]) % Q
                w[j + length] = (t - w[j + length]) % Q
                w[j + length] = (z * w[j + length]) % Q
                
            start = start + 2 * length
        length = length * 2
        
    # 21: f = 256^-1 mod q
    f = 8347681
    
    # FIPS se te cortó en la captura, pero el paso 22-23 es multiplicar todo por f
    for j in range(256):
        w[j] = (w[j] * f) % Q
        
    return w