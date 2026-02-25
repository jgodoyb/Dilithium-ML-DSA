# src/mldsa/mldsa.py
import os
import hashlib
from mldsa.core import keygen_internal, sign_internal, verify_internal

# Función auxiliar para IntegerToBytes(x, 1) usada en los prefijos
def _int_to_byte(val: int) -> bytes:
    return bytes([val])

# --- OIDs en formato DER (Distinguished Encoding Rules) para las variantes Pre-Hash ---
# Definidos en el Algoritmo 4 y 5 del FIPS 204
OID_SHA256 = bytes([0x06, 0x09, 0x60, 0x86, 0x48, 0x01, 0x65, 0x03, 0x04, 0x02, 0x01])
OID_SHA512 = bytes([0x06, 0x09, 0x60, 0x86, 0x48, 0x01, 0x65, 0x03, 0x04, 0x02, 0x03])
OID_SHAKE128 = bytes([0x06, 0x09, 0x60, 0x86, 0x48, 0x01, 0x65, 0x03, 0x04, 0x02, 0x0B])

# =============================================================================
# ALGORITMO 1: ML-DSA.KeyGen()
# =============================================================================
def keygen(level: str = "ML_DSA_65") -> tuple[bytes, bytes]:
    """Genera un par de claves (pk, sk)."""
    # 1: xi <- B^32 (Entropía aleatoria del sistema)
    xi = os.urandom(32)
    # 2-4: Manejo de errores de entropía (os.urandom lanzaría excepción si falla)
    # 5: return ML-DSA.KeyGen_internal(xi)
    return keygen_internal(xi, level=level)

# =============================================================================
# ALGORITMO 2: ML-DSA.Sign(sk, M, ctx)
# =============================================================================
def sign(sk: bytes, M: bytes, ctx: bytes = b"", level: str = "ML_DSA_65") -> bytes:
    """Firma un mensaje M (variante pura)."""
    # 1-3: if |ctx| > 255 then return perpendicular
    if len(ctx) > 255:
        raise ValueError("El contexto no puede exceder los 255 bytes.")
    
    # 5: rnd <- B^32 (Variante hedged por defecto)
    rnd = os.urandom(32)
    
    # 10: M' <- 0 || len(ctx) || ctx || M
    m_prime = _int_to_byte(0) + _int_to_byte(len(ctx)) + ctx + M
    
    # 11: sigma <- ML-DSA.Sign_internal(sk, M', rnd)
    return sign_internal(sk, m_prime, rnd, level=level)

# =============================================================================
# ALGORITMO 3: ML-DSA.Verify(pk, M, sigma, ctx)
# =============================================================================
def verify(pk: bytes, M: bytes, sigma: bytes, ctx: bytes = b"", level: str = "ML_DSA_65") -> bool:
    """Verifica una firma (variante pura)."""
    # 1-3: if |ctx| > 255 then return perpendicular
    if len(ctx) > 255:
        return False
        
    # 5: M' <- 0 || len(ctx) || ctx || M
    m_prime = _int_to_byte(0) + _int_to_byte(len(ctx)) + ctx + M
    
    # 6: return ML-DSA.Verify_internal(pk, M', sigma)
    return verify_internal(pk, m_prime, sigma, level=level)

# =============================================================================
# ALGORITMO 4: HashML-DSA.Sign(sk, M, ctx, PH)
# =============================================================================
def hash_sign(sk: bytes, M: bytes, ph_algo: str, ctx: bytes = b"", level: str = "ML_DSA_65") -> bytes:
    """Firma un mensaje usando la variante Pre-Hash (HashML-DSA)."""
    # 1-3:
    if len(ctx) > 255:
        raise ValueError("El contexto no puede exceder los 255 bytes.")
        
    # 5: rnd <- B^32
    rnd = os.urandom(32)
    
    # 10-22: switch PH do
    ph_algo = ph_algo.upper()
    if ph_algo == "SHA-256":
        oid = OID_SHA256
        ph_m = hashlib.sha256(M).digest()
    elif ph_algo == "SHA-512":
        oid = OID_SHA512
        ph_m = hashlib.sha512(M).digest()
    elif ph_algo == "SHAKE128":
        oid = OID_SHAKE128
        # SHAKE128(M, 256) significa 256 BITS de salida -> 32 bytes
        ph_m = hashlib.shake_128(M).digest(32) 
    else:
        raise ValueError(f"Algoritmo Pre-Hash no soportado: {ph_algo}")
        
    # 23: M' <- 1 || len(ctx) || ctx || OID || PH_M
    m_prime = _int_to_byte(1) + _int_to_byte(len(ctx)) + ctx + oid + ph_m
    
    # 24: sigma <- ML-DSA.Sign_internal(sk, M', rnd)
    return sign_internal(sk, m_prime, rnd, level=level)

# =============================================================================
# ALGORITMO 5: HashML-DSA.Verify(pk, M, sigma, ctx, PH)
# =============================================================================
def hash_verify(pk: bytes, M: bytes, sigma: bytes, ph_algo: str, ctx: bytes = b"", level: str = "ML_DSA_65") -> bool:
    """Verifica una firma usando la variante Pre-Hash (HashML-DSA)."""
    # 1-3:
    if len(ctx) > 255:
        return False
        
    # 5-17: switch PH do
    ph_algo = ph_algo.upper()
    if ph_algo == "SHA-256":
        oid = OID_SHA256
        ph_m = hashlib.sha256(M).digest()
    elif ph_algo == "SHA-512":
        oid = OID_SHA512
        ph_m = hashlib.sha512(M).digest()
    elif ph_algo == "SHAKE128":
        oid = OID_SHAKE128
        ph_m = hashlib.shake_128(M).digest(32)
    else:
        return False
        
    # 18: M' <- 1 || len(ctx) || ctx || OID || PH_M
    m_prime = _int_to_byte(1) + _int_to_byte(len(ctx)) + ctx + oid + ph_m
    
    # 19: return ML-DSA.Verify_internal(pk, M', sigma)
    return verify_internal(pk, m_prime, sigma, level=level)