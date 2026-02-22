# src/mldsa/sampling/samplers.py
from mldsa.crypto.hash_functions import H, G
from mldsa.sampling.sampling import coeff_from_three_bytes, coeff_from_half_byte
from mldsa.primitives.conversions import bytes_to_bits, integer_to_bytes
from mldsa.encoding.bitpacking import bit_unpack

def sample_in_ball(rho: bytes, tau: int) -> list:
    """
    Algoritmo 29: SampleInBall(rho)
    Genera un polinomio con coeficientes en {-1, 0, 1} y peso de Hamming tau.
    """
    c = [0] * 256
    ctx = H.Init()
    ctx = H.Absorb(ctx, rho)
    
    # Exprimimos los primeros 8 bytes para los signos
    ctx, s = H.Squeeze(ctx, 8)
    h = bytes_to_bits(s)
    
    # Bucle para repartir los coeficientes no nulos (Fisher-Yates shuffle)
    for i in range(256 - tau, 256):
        ctx, j_bytes = H.Squeeze(ctx, 1)
        j = j_bytes[0]
        
        # Muestreo de rechazo en {0, ..., i}
        while j > i:
            ctx, j_bytes = H.Squeeze(ctx, 1)
            j = j_bytes[0]
            
        c[i] = c[j]
        # (-1)^h[...] -> Si el bit es 0, da 1. Si es 1, da -1.
        bit_signo = h[i + tau - 256]
        c[j] = 1 if bit_signo == 0 else -1
        
    return c

def rej_ntt_poly(rho: bytes) -> list:
    """
    Algoritmo 30: RejNTTPoly(rho)
    Muestrea un polinomio aleatorio uniforme en T_q.
    """
    a_hat = [0] * 256
    j = 0
    ctx = G.Init()
    ctx = G.Absorb(ctx, rho)
    
    while j < 256:
        ctx, s = G.Squeeze(ctx, 3)
        # Intentamos obtener un coeficiente a partir de 3 bytes
        coeff = coeff_from_three_bytes(s[0], s[1], s[2])
        
        # Si no devuelve None (símbolo de rechazo de FIPS), lo guardamos
        if coeff is not None:
            a_hat[j] = coeff
            j += 1
            
    return a_hat

def rej_bounded_poly(rho: bytes, eta: int) -> list:
    """
    Algoritmo 31: RejBoundedPoly(rho)
    Muestrea un polinomio con coeficientes pequeños en [-eta, eta].
    """
    a = [0] * 256
    j = 0
    ctx = H.Init()
    ctx = H.Absorb(ctx, rho)
    
    while j < 256:
        ctx, z_bytes = H.Squeeze(ctx, 1)
        z = z_bytes[0]
        
        # Un byte nos da dos medios bytes (z0 y z1)
        z0 = coeff_from_half_byte(z % 16, eta)
        z1 = coeff_from_half_byte(z // 16, eta)
        
        if z0 is not None:
            a[j] = z0
            j += 1
        
        # Hay que comprobar que no nos hayamos pasado de 256 con el primer medio byte
        if z1 is not None and j < 256:
            a[j] = z1
            j += 1
            
    return a

def expand_mask(rho: bytes, mu: int, l: int, gamma1: int) -> list:
    """
    Algoritmo 34: ExpandMask(rho, mu)
    Muestrea un vector de l polinomios con coeficientes grandes.
    """
    # bitlen(gamma1 - 1). Como gamma1 es potencia de 2, gamma1-1 son todo unos.
    c = 1 + (gamma1 - 1).bit_length() 
    y = [None] * l
    
    for r in range(l):
        # rho' = rho || IntegerToBytes(mu + r, 2)
        rho_prime = rho + integer_to_bytes(mu + r, 2)
        
        # Llamada directa (digest) de 32 * c bytes
        v = H.digest(rho_prime, 32 * c)
        
        # Convertimos los bytes a coeficientes
        y[r] = bit_unpack(v, gamma1 - 1, gamma1)
        
    return y