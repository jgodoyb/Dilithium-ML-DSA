# src/tests/test_sampling/test_sampling.py
import unittest
import sys
import os

# "Puente" para encontrar el paquete mldsa desde la carpeta de tests
ruta_raiz = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if ruta_raiz not in sys.path:
    sys.path.insert(0, ruta_raiz)

from mldsa.sampling.sampling import coeff_from_three_bytes, coeff_from_half_byte
from mldsa.constants import Q

class TestSamplingFIPS204(unittest.TestCase):

    def test_alg14_coeff_from_three_bytes(self):
        """Prueba el Algoritmo 14: CoeffFromThreeBytes"""
        # Caso 1: Valor mínimo (0,0,0) -> 0
        self.assertEqual(coeff_from_three_bytes(0, 0, 0), 0)
        
        # Caso 2: Limpieza de bit superior (b2 = 128 es 10000000 en binario)
        # El algoritmo debe poner el bit 7 a cero, convirtiendo 128 en 0.
        self.assertEqual(coeff_from_three_bytes(1, 0, 128), 1)
        
        # Caso 3: Valor máximo aceptado (un poco menos que Q)
        # Q es 8380417. Probamos con algo justo debajo.
        self.assertIsNotNone(coeff_from_three_bytes(0, 0, 127)) # 127*2^16 es < Q
        
        # Caso 4: RECHAZO (z >= Q)
        # (255, 255, 127) da 8.388.607, que es > 8.380.417 (Q)
        self.assertIsNone(coeff_from_three_bytes(255, 255, 127))

    def test_alg15_coeff_from_half_byte_eta2(self):
        """Prueba el Algoritmo 15 con eta = 2"""
        # Caso aceptado: b=0 -> 2 - (0 mod 5) = 2
        self.assertEqual(coeff_from_half_byte(0, 2), 2)
        # Caso aceptado: b=14 -> 2 - (14 mod 5) = 2 - 4 = -2
        self.assertEqual(coeff_from_half_byte(14, 2), -2)
        # Caso RECHAZO: b >= 15
        self.assertIsNone(coeff_from_half_byte(15, 2))

    def test_alg15_coeff_from_half_byte_eta4(self):
        """Prueba el Algoritmo 15 con eta = 4"""
        # Caso aceptado: b=0 -> 4 - 0 = 4
        self.assertEqual(coeff_from_half_byte(0, 4), 4)
        # Caso aceptado: b=8 -> 4 - 8 = -4
        self.assertEqual(coeff_from_half_byte(8, 4), -4)
        # Caso RECHAZO: b >= 9
        self.assertIsNone(coeff_from_half_byte(9, 4))
        self.assertIsNone(coeff_from_half_byte(15, 4))

if __name__ == '__main__':
    unittest.main()