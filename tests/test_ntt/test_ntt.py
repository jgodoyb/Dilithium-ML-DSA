# src/tests/test_ntt/test_ntt.py
import unittest
import sys
import os
import random

ruta_raiz = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if ruta_raiz not in sys.path:
    sys.path.insert(0, ruta_raiz)

from mldsa.ntt.ntt import ntt, ntt_inv
from mldsa.ntt.operations import add_ntt
from mldsa.constants import Q

class TestNTTTransformations(unittest.TestCase):

    def test_ntt_roundtrip_zeros(self):
        """Caso base: El polinomio cero debe seguir siendo cero en el dominio NTT"""
        w = [0] * 256
        w_hat = ntt(w)
        self.assertEqual(w_hat, [0] * 256)
        
        w_recuperado = ntt_inv(w_hat)
        self.assertEqual(w, w_recuperado)

    def test_ntt_roundtrip_random_stress(self):
        """Prueba de estrés: 100 polinomios aleatorios de ida y vuelta"""
        for _ in range(100):
            w_original = [random.randint(0, Q - 1) for _ in range(256)]
            
            # NTT (ida) y NTT Inversa (vuelta)
            w_hat = ntt(w_original)
            w_recuperado = ntt_inv(w_hat)
            
            self.assertEqual(w_original, w_recuperado, "Error de redondeo o desbordamiento en la NTT")
            
            # Verifica que todos los coeficientes del dominio NTT estén dentro de [0, Q-1]
            self.assertTrue(all(0 <= c < Q for c in w_hat))

    def test_ntt_linearity(self):
        """Propiedad matemática: NTT(a + b) == NTT(a) + NTT(b)"""
        a = [random.randint(0, Q - 1) for _ in range(256)]
        b = [random.randint(0, Q - 1) for _ in range(256)]
        
        # 1. Sumamos en dominio normal y luego hacemos NTT
        a_plus_b = [(a[i] + b[i]) % Q for i in range(256)]
        ntt_suma = ntt(a_plus_b)
        
        # 2. Hacemos NTT primero y luego sumamos en el dominio NTT
        ntt_a = ntt(a)
        ntt_b = ntt(b)
        suma_ntts = add_ntt(ntt_a, ntt_b)
        
        self.assertEqual(ntt_suma, suma_ntts, "La NTT debe ser una operación estrictamente lineal")

if __name__ == '__main__':
    unittest.main()