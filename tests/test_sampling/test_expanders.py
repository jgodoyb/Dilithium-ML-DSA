# src/tests/test_sampling/test_expanders.py
import unittest
import sys
import os

ruta_raiz = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if ruta_raiz not in sys.path:
    sys.path.insert(0, ruta_raiz)

from mldsa.sampling.expanders import expand_a, expand_s
from mldsa.constants import Q
from mldsa.parameters import ML_DSA_PARAMS
ML_DSA_65 = ML_DSA_PARAMS["ML_DSA_65"]

class TestExpanders(unittest.TestCase):

    def setUp(self):
        self.rho = b'\x11' * 32
        self.rho_prime = b'\x22' * 64
        # Cargamos los parámetros dinámicamente
        self.k = ML_DSA_65["k"]
        self.l = ML_DSA_65["l"]
        self.eta = ML_DSA_65["eta"]

    def test_expand_a(self):
        A_hat = expand_a(self.rho, self.k, self.l)
        self.assertEqual(len(A_hat), self.k)
        for r in range(self.k):
            self.assertEqual(len(A_hat[r]), self.l)
            for s in range(self.l):
                poly = A_hat[r][s]
                self.assertEqual(len(poly), 256)
                self.assertTrue(all(0 <= x < Q for x in poly))

    def test_expand_s(self):
        s1, s2 = expand_s(self.rho_prime, self.k, self.l, self.eta)
        self.assertEqual(len(s1), self.l)
        self.assertEqual(len(s2), self.k)
        for poly in s1:
            self.assertEqual(len(poly), 256)
            self.assertTrue(all(-self.eta <= x <= self.eta for x in poly))
        for poly in s2:
            self.assertEqual(len(poly), 256)
            self.assertTrue(all(-self.eta <= x <= self.eta for x in poly))

if __name__ == '__main__':
    unittest.main()