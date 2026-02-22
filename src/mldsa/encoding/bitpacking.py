# src/mldsa/encoding/bitpacking.py
import math
from mldsa.primitives.conversions import integer_to_bits, bits_to_bytes, bytes_to_bits, bits_to_integer

def bitlen(x: int) -> int:
    """
    Función auxiliar: Calcula la longitud en bits de un entero 'x'.
    Según FIPS 204, bitlen(0) = 0.
    """
    if x == 0:
        return 0
    return x.bit_length()

def simple_bit_pack(w: list, b: int) -> bytes:
    """
    Algoritmo 16: SimpleBitPack(w, b)
    Codifica un polinomio w (lista de 256 coeficientes en [0, b]) en una cadena de bytes.
    """
    c = bitlen(b)
    z = [] # Usamos una lista para acumular los bits
    for i in range(256):
        # Concatenamos los bits de cada coeficiente
        z.extend(integer_to_bits(w[i], c))
    return bits_to_bytes(z)

def simple_bit_unpack(v: bytes, b: int) -> list:
    """
    Algoritmo 18: SimpleBitUnpack(v, b)
    Revierte el procedimiento SimpleBitPack.
    """
    c = bitlen(b)
    z = bytes_to_bits(v)
    w = [0] * 256
    for i in range(256):
        # Tomamos el bloque de 'c' bits correspondiente al coeficiente 'i'
        bloque_bits = z[i*c : (i+1)*c]
        w[i] = bits_to_integer(bloque_bits)
    return w

def bit_pack(w: list, a: int, b: int) -> bytes:
    """
    Algoritmo 17: BitPack(w, a, b)
    Codifica un polinomio w (coeficientes en [-a, b]) en una cadena de bytes.
    """
    c = bitlen(a + b)
    z = []
    for i in range(256):
        # Codificamos (b - wi)
        valor_a_codificar = b - w[i]
        z.extend(integer_to_bits(valor_a_codificar, c))
    return bits_to_bytes(z)

def bit_unpack(v: bytes, a: int, b: int) -> list:
    """
    Algoritmo 19: BitUnpack(v, a, b)
    Revierte el procedimiento BitPack.
    """
    c = bitlen(a + b)
    z = bytes_to_bits(v)
    w = [0] * 256
    for i in range(256):
        bloque_bits = z[i*c : (i+1)*c]
        # wi = b - BitsToInteger(...)
        w[i] = b - bits_to_integer(bloque_bits)
    return w