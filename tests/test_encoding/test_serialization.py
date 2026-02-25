# src/tests/test_encoding/test_serialization.py
import unittest
import sys
import os
import random

ruta_raiz = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if ruta_raiz not in sys.path:
    sys.path.insert(0, ruta_raiz)

from mldsa.encoding.serialization import (
    pk_encode, pk_decode,
    sk_encode, sk_decode,
    sig_encode, sig_decode
)

# 1. Importamos la constante universal Q
from mldsa.constants import Q
# 2. Importamos el diccionario de parámetros
from mldsa.parameters.registry import get_parameters

class TestSerialization(unittest.TestCase):

    def setUp(self):
        # Generadores de bytes aleatorios
        self.rho = os.urandom(32)
        self.K_seed = os.urandom(32)
        self.tr = os.urandom(64) 

    def generar_polinomio(self, min_val, max_val):
        return [random.randint(min_val, max_val) for _ in range(256)]

    def test_public_key_roundtrip(self):
        for level in ["ML_DSA_44", "ML_DSA_65", "ML_DSA_87"]:
            with self.subTest(level=level):
                p = get_parameters(level)
                d, k = p["d"], p["k"]
                limite_t1 = (2**(23 - d)) - 1 # bitlen(Q-1) es 23
                t1_original = [self.generar_polinomio(0, limite_t1) for _ in range(k)]
                
                pk_bytes = pk_encode(self.rho, t1_original, d)
                rho_recuperado, t1_recuperado = pk_decode(pk_bytes, k, d)
                
                self.assertEqual(self.rho, rho_recuperado)
                self.assertEqual(t1_original, t1_recuperado)

    def test_secret_key_roundtrip(self):
        for level in ["ML_DSA_44", "ML_DSA_65", "ML_DSA_87"]:
            with self.subTest(level=level):
                p = get_parameters(level)
                k, l, eta, d = p["k"], p["l"], p["eta"], p["d"]

                s1_orig = [self.generar_polinomio(-eta, eta) for _ in range(l)]
                s2_orig = [self.generar_polinomio(-eta, eta) for _ in range(k)]
                
                limite_inf_t0 = -(2**(d - 1)) + 1
                limite_sup_t0 = 2**(d - 1)
                t0_orig = [self.generar_polinomio(limite_inf_t0, limite_sup_t0) for _ in range(k)]
                
                sk_bytes = sk_encode(self.rho, self.K_seed, self.tr, s1_orig, s2_orig, t0_orig, eta, d)
                rho_rec, K_rec, tr_rec, s1_rec, s2_rec, t0_rec = sk_decode(sk_bytes, k, l, eta, d)
                
                self.assertEqual(self.rho, rho_rec)
                self.assertEqual(s1_orig, s1_rec)
                self.assertEqual(s2_orig, s2_rec)
                self.assertEqual(t0_orig, t0_rec)

    def test_signature_roundtrip(self):
        for level in ["ML_DSA_44", "ML_DSA_65", "ML_DSA_87"]:
            with self.subTest(level=level):
                p = get_parameters(level)
                l, k, gamma1, omega, c_tilde_len = p["l"], p["k"], p["gamma_1"], p["omega"], p["c_tilde_bytes"]
                c_tilde = os.urandom(c_tilde_len)

                z_orig = [self.generar_polinomio(-(gamma1 - 1), gamma1) for _ in range(l)]
                
                h_orig = [[0] * 256 for _ in range(k)]
                for _ in range(20):
                    h_orig[random.randint(0, k - 1)][random.randint(0, 255)] = 1
                    
                sig_bytes = sig_encode(c_tilde, z_orig, h_orig, gamma1, omega, k)
                c_rec, z_rec, h_rec = sig_decode(sig_bytes, l, gamma1, omega, k, c_tilde_len)
                
                self.assertEqual(c_tilde, c_rec)
                self.assertEqual(z_orig, z_rec)
                self.assertEqual(h_orig, h_rec)

if __name__ == '__main__':
    unittest.main()