# src/mldsa/encoding/serialization.py
from mldsa.constants import Q
from mldsa.encoding.bitpacking import simple_bit_pack, simple_bit_unpack, bit_pack, bit_unpack
from mldsa.encoding.complex_structures import hint_bit_pack, hint_bit_unpack

def bitlen(x: int) -> int:
    return x.bit_length() if x != 0 else 0

# ==========================================
# CLAVE PÚBLICA (Public Key)
# ==========================================
def pk_encode(rho: bytes, t1: list, d: int) -> bytes:
    """Algoritmo 22: pkEncode. Empaqueta la clave pública."""
    pk = bytearray(rho)
    limite = (2**(bitlen(Q - 1) - d)) - 1
    
    for poly in t1:
        pk.extend(simple_bit_pack(poly, limite))
    return bytes(pk)

def pk_decode(pk: bytes, k: int, d: int) -> tuple:
    """Algoritmo 23: pkDecode. Recupera rho y t1."""
    rho = pk[0:32]
    t1 = []
    
    limite = (2**(bitlen(Q - 1) - d)) - 1
    chunk_size = 32 * bitlen(limite)
    
    offset = 32
    for _ in range(k):
        chunk = pk[offset : offset + chunk_size]
        t1.append(simple_bit_unpack(chunk, limite))
        offset += chunk_size
        
    return rho, t1

# ==========================================
# CLAVE PRIVADA (Secret Key)
# ==========================================
def sk_encode(rho: bytes, K: bytes, tr: bytes, s1: list, s2: list, t0: list, eta: int, d: int) -> bytes:
    """Algoritmo 24: skEncode. Empaqueta la clave privada."""
    sk = bytearray(rho + K + tr)
    
    for poly in s1:
        sk.extend(bit_pack(poly, eta, eta))
    for poly in s2:
        sk.extend(bit_pack(poly, eta, eta))
    for poly in t0:
        sk.extend(bit_pack(poly, (2**(d-1)) - 1, 2**(d-1)))
        
    return bytes(sk)

def sk_decode(sk: bytes, k: int, l: int, eta: int, d: int) -> tuple:
    """Algoritmo 25: skDecode. Recupera rho, K, tr, s1, s2, t0."""
    rho = sk[0:32]
    K = sk[32:64]
    tr = sk[64:128]
    
    s1, s2, t0 = [], [], []
    offset = 128
    
    # Decodificar s1
    chunk_size_s = 32 * bitlen(2 * eta)
    for _ in range(l):
        chunk = sk[offset : offset + chunk_size_s]
        s1.append(bit_unpack(chunk, eta, eta))
        offset += chunk_size_s
        
    # Decodificar s2
    for _ in range(k):
        chunk = sk[offset : offset + chunk_size_s]
        s2.append(bit_unpack(chunk, eta, eta))
        offset += chunk_size_s
        
    # Decodificar t0
    chunk_size_t0 = 32 * d
    for _ in range(k):
        chunk = sk[offset : offset + chunk_size_t0]
        t0.append(bit_unpack(chunk, (2**(d-1)) - 1, 2**(d-1)))
        offset += chunk_size_t0
        
    return rho, K, tr, s1, s2, t0

# ==========================================
# FIRMA (Signature)
# ==========================================
def sig_encode(c_tilde: bytes, z: list, h: list, gamma1: int, omega: int, k: int) -> bytes:
    """Algoritmo 26: sigEncode. Empaqueta la firma."""
    sig = bytearray(c_tilde)
    
    for poly in z:
        sig.extend(bit_pack(poly, gamma1 - 1, gamma1))
        
    sig.extend(hint_bit_pack(h, omega, k))
    return bytes(sig)

def sig_decode(sig: bytes, l: int, gamma1: int, omega: int, k: int, c_tilde_len: int) -> tuple:
    """Algoritmo 27: sigDecode. Recupera c_tilde, z, h."""
    c_tilde = sig[0 : c_tilde_len]
    offset = c_tilde_len
    
    z = []
    chunk_size_z = 32 * (1 + bitlen(gamma1 - 1))
    for _ in range(l):
        chunk = sig[offset : offset + chunk_size_z]
        z.append(bit_unpack(chunk, gamma1 - 1, gamma1))
        offset += chunk_size_z
        
    h_bytes = sig[offset : offset + omega + k]
    h = hint_bit_unpack(h_bytes, omega, k)
    
    return c_tilde, z, h