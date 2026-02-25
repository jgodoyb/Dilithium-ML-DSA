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
from mldsa.parameters.registry import get_parameters

class TestRoundingFIPS204(unittest.TestCase):

    def test_mod_centered(self):
        alpha = 10
        self.assertEqual(mod_centered(2, alpha), 2)
        self.assertEqual(mod_centered(5, alpha), 5)
        self.assertEqual(mod_centered(6, alpha), -4)
        self.assertEqual(mod_centered(9, alpha), -1)

    def test_power2round_reconstruction(self):
        for _ in range(100):
            r = random.randint(0, Q - 1)
            for level in ["ML_DSA_44", "ML_DSA_65", "ML_DSA_87"]:
                with self.subTest(level=level):
                    d = get_parameters(level)["d"]
                    r1, r0 = power2round(r, d)
                    reconstruido = (r1 * (2**d) + r0) % Q
                    self.assertEqual(r, reconstruido)

    def test_power2round_polymorphism(self):
        r_poly = [random.randint(0, Q - 1) for _ in range(256)]
        for level in ["ML_DSA_44", "ML_DSA_65", "ML_DSA_87"]:
            with self.subTest(level=level):
                d = get_parameters(level)["d"]
                r1_poly, r0_poly = power2round(r_poly, d)
                reconstruido_0 = (r1_poly[0] * (2**d) + r0_poly[0]) % Q
                self.assertEqual(r_poly[0], reconstruido_0)

    def test_decompose_edge_case(self):
        r = Q - 1
        for level in ["ML_DSA_44", "ML_DSA_65", "ML_DSA_87"]:
            with self.subTest(level=level):
                gamma2 = get_parameters(level)["gamma_2"]
                r1, r0 = decompose(r, gamma2)
                self.assertEqual(r1, 0)
                self.assertEqual(r0, -1)

    def test_hint_magic_property(self):
        for level in ["ML_DSA_44", "ML_DSA_65", "ML_DSA_87"]:
            with self.subTest(level=level):
                gamma2 = get_parameters(level)["gamma_2"]
                r_poly = [random.randint(0, Q - 1) for _ in range(256)]
                z_poly = [random.randint(-gamma2 // 2, gamma2 // 2) for _ in range(256)]
                
                h_poly = make_hint(z_poly, r_poly, gamma2)
                recovered_r1_poly = use_hint(h_poly, r_poly, gamma2)
                
                r_plus_z = [(r_poly[i] + z_poly[i]) % Q for i in range(256)]
                expected_r1_poly = highbits(r_plus_z, gamma2)
                
                self.assertEqual(recovered_r1_poly, expected_r1_poly)

if __name__ == '__main__':
    unittest.main()