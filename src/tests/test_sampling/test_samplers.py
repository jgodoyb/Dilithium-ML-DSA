# src/tests/test_sampling/test_samplers.py
import unittest
import sys
import os

ruta_raiz = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if ruta_raiz not in sys.path:
    sys.path.insert(0, ruta_raiz)

from mldsa.sampling.samplers import sample_in_ball, rej_ntt_poly, rej_bounded_poly, expand_mask
from mldsa.constants import Q
from mldsa.parameters.mldsa65 import ML_DSA_65

class TestSamplers(unittest.TestCase):

    def setUp(self):
        self.rho_32 = b'\xab' * 32
        self.rho_64 = b'\xcd' * 64
        # Cargamos los parámetros
        self.tau = ML_DSA_65["tau"]
        self.l = ML_DSA_65["l"]
        self.gamma1 = ML_DSA_65["gamma_1"]

    def test_sample_in_ball(self):
        c = sample_in_ball(self.rho_32, self.tau)
        self.assertEqual(len(c), 256)
        valores_unicos = set(c)
        self.assertTrue(valores_unicos.issubset({-1, 0, 1}))
        peso_hamming = sum(1 for x in c if x != 0)
        self.assertEqual(peso_hamming, self.tau)

    def test_rej_ntt_poly(self):
        a_hat = rej_ntt_poly(self.rho_32)
        self.assertEqual(len(a_hat), 256)
        self.assertTrue(all(0 <= x < Q for x in a_hat))

    def test_rej_bounded_poly(self):
        # Eta es 2 o 4 dependiendo de la fase, probamos ambas genéricamente
        for eta in [2, 4]:
            a = rej_bounded_poly(self.rho_64, eta)
            self.assertEqual(len(a), 256)
            self.assertTrue(all(-eta <= x <= eta for x in a))

    def test_expand_mask(self):
        mu = 0
        y = expand_mask(self.rho_64, mu, self.l, self.gamma1)
        self.assertEqual(len(y), self.l)
        for poly in y:
            self.assertEqual(len(poly), 256)
            self.assertTrue(all(-(self.gamma1 - 1) <= x <= self.gamma1 for x in poly))

if __name__ == '__main__':
    unittest.main()