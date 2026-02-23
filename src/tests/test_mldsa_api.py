# src/tests/test_mldsa_api.py
import unittest
import sys
import os

# Asegurar que el proyecto sea importable
ruta_raiz = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ruta_raiz not in sys.path:
    sys.path.insert(0, ruta_raiz)

# Importamos directamente desde tu __init__.py público
from mldsa import keygen, sign, verify, hash_sign, hash_verify

class TestMLDSA_API(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Generamos las claves una sola vez para acelerar todos los tests."""
        print("Generando par de claves para los tests de API... (puede tardar un segundo)")
        cls.pk, cls.sk = keygen()
        cls.msg = b"Mensaje confidencial de prueba"

    def test_pure_sign_verify_no_ctx(self):
        """1. Prueba de ML-DSA Puro (Algoritmos 2 y 3) sin contexto."""
        sig = sign(self.sk, self.msg)
        
        # Debe verificar correctamente
        self.assertTrue(verify(self.pk, self.msg, sig), "La firma pura falló en la verificación.")
        
        # Debe fallar si alteramos el mensaje
        self.assertFalse(verify(self.pk, b"Mensaje modificado", sig), "Aceptó un mensaje alterado.")

    def test_pure_sign_verify_with_ctx(self):
        """2. Prueba de la funcionalidad de Contexto (Domain Separation)."""
        ctx_facturas = b"Contexto: Facturas 2026"
        ctx_contratos = b"Contexto: Contratos"
        
        # Firmamos con el contexto de facturas
        sig = sign(self.sk, self.msg, ctx=ctx_facturas)
        
        # 2a. Verifica bien con el mismo contexto
        self.assertTrue(verify(self.pk, self.msg, sig, ctx=ctx_facturas))
        
        # 2b. FALLA si usamos un contexto diferente
        self.assertFalse(verify(self.pk, self.msg, sig, ctx=ctx_contratos))
        
        # 2c. FALLA si intentamos verificar sin contexto
        self.assertFalse(verify(self.pk, self.msg, sig))

    def test_context_length_limit(self):
        """3. Prueba que se respete el límite estricto de 255 bytes para el contexto."""
        ctx_invalido = b"X" * 256
        
        # sign() debe lanzar una excepción
        with self.assertRaises(ValueError):
            sign(self.sk, self.msg, ctx=ctx_invalido)
            
        # verify() debe simplemente retornar False
        sig_dummy = sign(self.sk, self.msg) # Firma válida normal
        self.assertFalse(verify(self.pk, self.msg, sig_dummy, ctx=ctx_invalido))

    def test_hash_sign_verify(self):
        """4. Prueba de las variantes HashML-DSA (Algoritmos 4 y 5) con varios algoritmos."""
        algoritmos = ["SHA-256", "SHA-512", "SHAKE128", "sha-256"] # El último prueba case-insensitive
        
        for algo in algoritmos:
            sig = hash_sign(self.sk, self.msg, ph_algo=algo)
            
            # 4a. Verifica bien con el algoritmo correcto
            self.assertTrue(hash_verify(self.pk, self.msg, sig, ph_algo=algo), 
                            f"Falló HashML-DSA con {algo}")
            
            # 4b. FALLA si intentamos verificar diciendo que se usó otro algoritmo
            algo_erroneo = "SHA-512" if algo.upper() == "SHA-256" else "SHA-256"
            self.assertFalse(hash_verify(self.pk, self.msg, sig, ph_algo=algo_erroneo))

    def test_domain_separation_pure_vs_hash(self):
        """
        5. Prueba crítica de seguridad: Una firma Pura NO puede ser validada
        como Pre-Hash, y viceversa (por el prefijo 0x00 vs 0x01).
        """
        # Firma pura
        sig_pure = sign(self.sk, self.msg)
        # Firma pre-hash
        sig_hash = hash_sign(self.sk, self.msg, ph_algo="SHA-256")
        
        # Intento de ataque de confusión de dominio
        self.assertFalse(hash_verify(self.pk, self.msg, sig_pure, ph_algo="SHA-256"), 
                         "¡ALERTA! Firma pura validada como HashML-DSA.")
        self.assertFalse(verify(self.pk, self.msg, sig_hash), 
                         "¡ALERTA! Firma HashML-DSA validada como pura.")

if __name__ == '__main__':
    unittest.main()