# src/tests/test_crypto/test_hash_functions.py
import unittest
import sys
import os
import random

ruta_raiz = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if ruta_raiz not in sys.path:
    sys.path.insert(0, ruta_raiz)

from mldsa.crypto.hash_functions import H, G

class TestHashFunctions(unittest.TestCase):

    def test_digest_basic(self):
        """Verifica que el digest básico devuelve la longitud correcta"""
        mensaje = b"Test de TFG"
        h_out = H.digest(mensaje, 32)
        g_out = G.digest(mensaje, 64)
        
        self.assertEqual(len(h_out), 32)
        self.assertEqual(len(g_out), 64)
        # H y G deben dar resultados distintos para la misma entrada
        self.assertNotEqual(h_out, g_out[:32])

    def test_fips_equivalence_H_shake256(self):
        """
        Verifica la equivalencia exacta descrita en FIPS 204:
        H.digest(str1 || str2, l1 + l2) == H.Squeeze(H.Absorb(H.Absorb(H.Init(), str1), str2))
        """
        str1 = b"Parte 1 del "
        str2 = b"mensaje a firmar."
        l1, l2 = 15, 33  # Longitudes arbitrarias
        
        # 1. Método de llamada única (Digest)
        mensaje_completo = str1 + str2
        salida_directa = H.digest(mensaje_completo, l1 + l2)
        
        # 2. Método Incremental (Esponja)
        ctx = H.Init()
        ctx = H.Absorb(ctx, str1)
        ctx = H.Absorb(ctx, str2)
        
        ctx, out1 = H.Squeeze(ctx, l1)
        ctx, out2 = H.Squeeze(ctx, l2)
        salida_incremental = out1 + out2
        
        # Deben ser bit a bit idénticos
        self.assertEqual(salida_directa, salida_incremental)

    def test_fips_equivalence_G_shake128(self):
        """Verifica la equivalencia FIPS para G (SHAKE128)"""
        str_data = b"Semilla aleatoria rho"
        
        salida_directa = G.digest(str_data, 100)
        
        ctx = G.Init()
        ctx = G.Absorb(ctx, str_data)
        
        # Exprimimos en trozos irregulares: 10, 20, 70 bytes
        ctx, out1 = G.Squeeze(ctx, 10)
        ctx, out2 = G.Squeeze(ctx, 20)
        ctx, out3 = G.Squeeze(ctx, 70)
        salida_incremental = out1 + out2 + out3
        
        self.assertEqual(salida_directa, salida_incremental)

    def test_context_independence(self):
        """Verifica que crear dos contextos a la vez no mezcla sus estados internos"""
        ctx1 = H.Init()
        ctx2 = H.Init()
        
        ctx1 = H.Absorb(ctx1, b"A")
        ctx2 = H.Absorb(ctx2, b"B")
        
        _, out1 = H.Squeeze(ctx1, 10)
        _, out2 = H.Squeeze(ctx2, 10)
        
        self.assertNotEqual(out1, out2)

if __name__ == '__main__':
    unittest.main()