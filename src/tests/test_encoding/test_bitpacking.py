# src/tests/test_encoding/test_bitpacking.py
import unittest
import sys
import os
import random

# Puente para encontrar el paquete mldsa desde la carpeta de tests
ruta_raiz = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if ruta_raiz not in sys.path:
    sys.path.insert(0, ruta_raiz)

from mldsa.encoding.bitpacking import (
    simple_bit_pack, simple_bit_unpack,
    bit_pack, bit_unpack
)

class TestBitPackingExtensive(unittest.TestCase):

    def test_simple_bit_pack_zeros(self):
        """Caso borde: Polinomio lleno de ceros"""
        b = 15
        w = [0] * 256
        v_bytes = simple_bit_pack(w, b)
        w_recuperado = simple_bit_unpack(v_bytes, b)
        
        self.assertEqual(w, w_recuperado)
        self.assertEqual(all(byte == 0 for byte in v_bytes), True)

    def test_simple_bit_pack_max_values(self):
        """Caso borde: Todos los coeficientes al límite máximo permitido (b)"""
        for bit_length in [4, 13, 18]:
            b = (2**bit_length) - 1
            w = [b] * 256
            v_bytes = simple_bit_pack(w, b)
            w_recuperado = simple_bit_unpack(v_bytes, b)
            
            self.assertEqual(w, w_recuperado, f"Fallo en max_values con bitlen {bit_length}")
            self.assertEqual(len(v_bytes), 32 * bit_length)

    def test_simple_bit_pack_random_iterations(self):
        """Prueba de estres: 50 polinomios aleatorios con diferentes b"""
        for _ in range(50):
            bit_size = random.randint(1, 20)
            b = (2**bit_size) - 1
            w_rand = [random.randint(0, b) for _ in range(256)]
            
            v_bytes = simple_bit_pack(w_rand, b)
            w_recuperado = simple_bit_unpack(v_bytes, b)
            self.assertEqual(w_rand, w_recuperado)

    def test_bit_pack_signed_ranges(self):
        """Prueba BitPack con rangos negativos y positivos ([-a, b])"""
        # Escenario 1: Rango de secretos eta=4 ([-4, 4])
        a1, b1 = 4, 4
        w1 = [random.randint(-a1, b1) for _ in range(256)]
        v1 = bit_pack(w1, a1, b1)
        self.assertEqual(w1, bit_unpack(v1, a1, b1))

        # Escenario 2: Rango asimétrico [-2, 10]
        a2, b2 = 2, 10
        w2 = [random.randint(-a2, b2) for _ in range(256)]
        v2 = bit_pack(w2, a2, b2)
        self.assertEqual(w2, bit_unpack(v2, a2, b2))

    def test_bit_pack_large_gamma(self):
        """Prueba con valores grandes (Gamma1 = 2^19)"""
        gamma1 = 2**19
        a, b = gamma1, gamma1
        w = [random.randint(-a, b) for _ in range(256)]
        
        v = bit_pack(w, a, b)
        # bitlen(2^19 + 2^19) = bitlen(2^20) = 21 bits por coeficiente
        # Tamaño esperado = 256 * 21 / 8 = 672 bytes
        self.assertEqual(len(v), 672)
        self.assertEqual(w, bit_unpack(v, a, b))

    def test_bit_unpack_preserves_bounds(self):
        """Verifica que el desempaquetado no desborda los límites bitlen"""
        b = 7 # 3 bits
        # Un byte string de 32*3 = 96 bytes llenos de 0xFF
        v_full = b'\xff' * 96 
        w = simple_bit_unpack(v_full, b)
        # Cada coeficiente no puede ser mayor que 2^3 - 1 = 7
        self.assertTrue(all(c <= 7 for c in w))

if __name__ == '__main__':
    unittest.main()