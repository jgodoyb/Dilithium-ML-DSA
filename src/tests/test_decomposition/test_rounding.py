# src/tests/test_decomposition/test_rounding.py
import unittest
import sys
import os
import random

ruta_raiz = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if ruta_raiz not in sys.path:
    sys.path.insert(0, ruta_raiz)

from mldsa.decomposition.rounding import (
    mod_centered, power2round, decompose, 
    highbits, lowbits, make_hint, use_hint
)
from mldsa.constants import Q
from mldsa.parameters.mldsa65 import ML_DSA_65

class TestRoundingFIPS204(unittest.TestCase):

    def setUp(self):
        # Parámetros dinámicos
        self.d = ML_DSA_65["d"]
        self.gamma2 = ML_DSA_65["gamma_2"]
        self.alpha = 2 * self.gamma2

    def test_mod_centered(self):
        alpha = 10
        self.assertEqual(mod_centered(2, alpha), 2)
        self.assertEqual(mod_centered(5, alpha), 5)
        self.assertEqual(mod_centered(6, alpha), -4)
        self.assertEqual(mod_centered(9, alpha), -1)

    def test_power2round_reconstruction(self):
        for _ in range(100):
            r = random.randint(0, Q - 1)
            r1, r0 = power2round(r, self.d)
            reconstruido = (r1 * (2**self.d) + r0) % Q
            self.assertEqual(r, reconstruido)

    def test_power2round_polymorphism(self):
        r_poly = [random.randint(0, Q - 1) for _ in range(256)]
        r1_poly, r0_poly = power2round(r_poly, self.d)
        reconstruido_0 = (r1_poly[0] * (2**self.d) + r0_poly[0]) % Q
        self.assertEqual(r_poly[0], reconstruido_0)

    def test_decompose_edge_case(self):
        r = Q - 1
        r1, r0 = decompose(r, self.gamma2)
        self.assertEqual(r1, 0)
        self.assertEqual(r0, -1)

    def test_hint_magic_property(self):
        r_poly = [random.randint(0, Q - 1) for _ in range(256)]
        z_poly = [random.randint(-self.gamma2 // 2, self.gamma2 // 2) for _ in range(256)]
        
        h_poly = make_hint(z_poly, r_poly, self.gamma2)
        recovered_r1_poly = use_hint(h_poly, r_poly, self.gamma2)
        
        r_plus_z = [(r_poly[i] + z_poly[i]) % Q for i in range(256)]
        expected_r1_poly = highbits(r_plus_z, self.gamma2)
        
        self.assertEqual(recovered_r1_poly, expected_r1_poly)

if __name__ == '__main__':
    unittest.main()