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
# 2. Importamos el diccionario de parámetros de ML-DSA-65
from mldsa.parameters.mldsa65 import ML_DSA_65

class TestSerialization(unittest.TestCase):

    def setUp(self):
        # Cargamos los parámetros desde tu diccionario
        self.k = ML_DSA_65["k"]
        self.l = ML_DSA_65["l"]
        self.eta = ML_DSA_65["eta"]
        self.d = ML_DSA_65["d"]
        self.gamma1 = ML_DSA_65["gamma_1"]
        self.omega = ML_DSA_65["omega"]
        self.c_tilde_len = ML_DSA_65["c_tilde_bytes"]
        
        # Generadores de bytes aleatorios
        self.rho = os.urandom(32)
        self.K_seed = os.urandom(32)
        self.tr = os.urandom(64)
        # Usamos la longitud exacta para c_tilde (48 bytes)
        self.c_tilde = os.urandom(self.c_tilde_len) 

    def generar_polinomio(self, min_val, max_val):
        return [random.randint(min_val, max_val) for _ in range(256)]

    def test_public_key_roundtrip(self):
        limite_t1 = (2**(23 - self.d)) - 1 # bitlen(Q-1) es 23
        t1_original = [self.generar_polinomio(0, limite_t1) for _ in range(self.k)]
        
        pk_bytes = pk_encode(self.rho, t1_original, self.d)
        rho_recuperado, t1_recuperado = pk_decode(pk_bytes, self.k, self.d)
        
        self.assertEqual(self.rho, rho_recuperado)
        self.assertEqual(t1_original, t1_recuperado)

    def test_secret_key_roundtrip(self):
        s1_orig = [self.generar_polinomio(-self.eta, self.eta) for _ in range(self.l)]
        s2_orig = [self.generar_polinomio(-self.eta, self.eta) for _ in range(self.k)]
        
        limite_inf_t0 = -(2**(self.d - 1)) + 1
        limite_sup_t0 = 2**(self.d - 1)
        t0_orig = [self.generar_polinomio(limite_inf_t0, limite_sup_t0) for _ in range(self.k)]
        
        sk_bytes = sk_encode(self.rho, self.K_seed, self.tr, s1_orig, s2_orig, t0_orig, self.eta, self.d)
        rho_rec, K_rec, tr_rec, s1_rec, s2_rec, t0_rec = sk_decode(sk_bytes, self.k, self.l, self.eta, self.d)
        
        self.assertEqual(self.rho, rho_rec)
        self.assertEqual(s1_orig, s1_rec)
        self.assertEqual(s2_orig, s2_rec)
        self.assertEqual(t0_orig, t0_rec)

    def test_signature_roundtrip(self):
        z_orig = [self.generar_polinomio(-(self.gamma1 - 1), self.gamma1) for _ in range(self.l)]
        
        h_orig = [[0] * 256 for _ in range(self.k)]
        for _ in range(20):
            h_orig[random.randint(0, self.k - 1)][random.randint(0, 255)] = 1
            
        sig_bytes = sig_encode(self.c_tilde, z_orig, h_orig, self.gamma1, self.omega, self.k)
        c_rec, z_rec, h_rec = sig_decode(sig_bytes, self.l, self.gamma1, self.omega, self.k, self.c_tilde_len)
        
        self.assertEqual(self.c_tilde, c_rec)
        self.assertEqual(z_orig, z_rec)
        self.assertEqual(h_orig, h_rec)

if __name__ == '__main__':
    unittest.main()