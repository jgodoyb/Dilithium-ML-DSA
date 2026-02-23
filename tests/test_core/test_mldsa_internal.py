# src/tests/test_core/test_mldsa_internal.py
import unittest
import sys
import os

# Asegurar que el proyecto sea importable
ruta_raiz = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if ruta_raiz not in sys.path:
    sys.path.insert(0, ruta_raiz)

from mldsa.core.mldsa_internal import keygen_internal, sign_internal, verify_internal

class TestMLDSAInternal(unittest.TestCase):

    def setUp(self):
        """Configuración inicial con semillas fijas para repetibilidad."""
        # Semilla xi para KeyGen (32 bytes)
        self.xi = b"seed_for_keygen_testing_32_bytes"
        # Mensaje a firmar
        self.message = b"Este es un mensaje de prueba para el TFG de ML-DSA"
        # rnd para firma (determinista en este test para control)
        self.rnd = b"\x00" * 32

    def test_complete_flow_success(self):
        """
        Prueba el camino feliz: Generación -> Firma -> Verificación.
        Debe retornar True.
        """
        # 1. Generar Claves
        pk, sk = keygen_internal(self.xi)
        self.assertIsNotNone(pk)
        self.assertIsNotNone(sk)

        # 2. Firmar
        sigma = sign_internal(sk, self.message, self.rnd)
        self.assertIsNotNone(sigma)

        # 3. Verificar
        es_valida = verify_internal(pk, self.message, sigma)
        self.assertTrue(es_valida, "La firma válida fue rechazada por el verificador.")

    def test_tampered_message_fails(self):
        """Prueba que si el mensaje cambia, la firma se vuelve inválida."""
        pk, sk = keygen_internal(self.xi)
        sigma = sign_internal(sk, self.message, self.rnd)

        # Mensaje alterado
        mensaje_falso = b"Este es un mensaje alterado"
        es_valida = verify_internal(pk, mensaje_falso, sigma)
        self.assertFalse(es_valida, "El sistema aceptó una firma para un mensaje modificado.")

    def test_tampered_signature_fails(self):
        """Prueba que si la firma cambia un solo bit, es rechazada."""
        pk, sk = keygen_internal(self.xi)
        sigma = sign_internal(sk, self.message, self.rnd)

        # Alterar el primer byte de la firma (el compromiso c_tilde)
        sigma_lista = bytearray(sigma)
        sigma_lista[0] ^= 0xFF 
        sigma_corrupta = bytes(sigma_lista)

        es_valida = verify_internal(pk, self.message, sigma_corrupta)
        self.assertFalse(es_valida, "El sistema aceptó una firma corrupta.")

    def test_different_keys_fail(self):
        """Prueba que una firma hecha con sk_A no valide con pk_B."""
        # Generar dos pares de claves distintos
        pk_a, sk_a = keygen_internal(os.urandom(32))
        pk_b, sk_b = keygen_internal(os.urandom(32))

        # Firmar con la clave A
        sigma_a = sign_internal(sk_a, self.message, self.rnd)

        # Intentar verificar con la clave pública B
        es_valida = verify_internal(pk_b, self.message, sigma_a)
        self.assertFalse(es_valida, "Una firma de Alice fue validada con la clave de Bob.")

if __name__ == '__main__':
    # Temperatura 0: No queremos aleatoriedad en los errores, queremos precisión.
    unittest.main()