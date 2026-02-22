# src/mldsa/primitives/conversions.py

def integer_to_bits(x: int, alpha: int) -> list:
    """
    Algoritmo 9: IntegerToBits(x, alpha).
    Convierte un entero x en una cadena de bits de longitud alpha.
    """
    x_prime = x
    y = [0] * alpha
    for i in range(alpha):
        y[i] = x_prime % 2
        x_prime = x_prime // 2
    return y

def bits_to_integer(y: list) -> int:
    """
    Algoritmo 10: BitsToInteger(y).
    Convierte una cadena de bits en un entero usando orden little-endian.
    """
    x = 0
    alpha = len(y)
    for i in range(1, alpha + 1):
        x = 2 * x + y[alpha - i]
    return x

def integer_to_bytes(x: int, alpha: int) -> bytes:
    """
    Algoritmo 11: IntegerToBytes(x, alpha).
    Convierte un entero x en una cadena de bytes de longitud alpha.
    """
    x_prime = x
    y = bytearray(alpha)
    for i in range(alpha):
        y[i] = x_prime % 256
        x_prime = x_prime // 256
    return bytes(y)

def bits_to_bytes(y: list) -> bytes:
    """
    Algoritmo 12: BitsToBytes(y).
    Convierte una cadena de bits en una cadena de bytes.
    """
    alpha = len(y)
    z_len = (alpha + 7) // 8  # Equivalente a ceil(alpha/8)
    z = bytearray(z_len)
    for i in range(alpha):
        z[i // 8] = z[i // 8] + y[i] * (2**(i % 8))
    return bytes(z)

def bytes_to_bits(z: bytes) -> list:
    """
    Algoritmo 13: BytesToBits(z).
    Convierte una cadena de bytes en una cadena de bits.
    """
    alpha = len(z)
    y = [0] * (8 * alpha)
    z_prime = list(z)
    for i in range(alpha):
        for j in range(8):
            y[8 * i + j] = z_prime[i] % 2
            z_prime[i] = z_prime[i] // 2
    return y

def bit_rev_8(m: int) -> int:
    """
    Algoritmo 43: BitRev8(m).
    Inversion de los 8 bits de un byte.
    """
    # Paso 1: b <- IntegerToBits(m, 8)
    b = integer_to_bits(m, 8)
    
    # Pasos 2-5: El bucle de inversion
    b_rev = [0] * 8
    for i in range(8):
        b_rev[i] = b[7 - i]
    
    # Paso 6: r <- BitsToInteger(b_rev)
    r = bits_to_integer(b_rev)
    return r