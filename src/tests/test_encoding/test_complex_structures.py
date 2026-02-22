# src/tests/test_encoding/test_complex_structures.py
import unittest
import sys
import os
import random

ruta_raiz = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if ruta_raiz not in sys.path:
    sys.path.insert(0, ruta_raiz)

from mldsa.encoding.complex_structures import hint_bit_pack, hint_bit_unpack, w1_encode
from mldsa.constants import Q
# IMPORTAMOS LOS PARÁMETROS DESDE TU DICCIONARIO
from mldsa.parameters.mldsa65 import ML_DSA_65

class TestComplexStructures(unittest.TestCase):

    def setUp(self):
        # Parámetros cargados dinámicamente para ML-DSA-65
        self.k = ML_DSA_65["k"]
        self.omega = ML_DSA_65["omega"]
        self.gamma2 = ML_DSA_65["gamma_2"]

    def generar_hint_valido(self, total_unos):
        """Genera un vector h válido con exactamente 'total_unos' repartidos."""
        h = [[0] * 256 for _ in range(self.k)]
        unos_colocados = 0
        while unos_colocados < total_unos:
            i = random.randint(0, self.k - 1)
            j = random.randint(0, 255)
            if h[i][j] == 0:
                h[i][j] = 1
                unos_colocados += 1
        return h

    def test_hint_bit_pack_roundtrip(self):
        """Verifica que un vector de pistas válido se empaqueta y desempaqueta perfectamente."""
        h_original = self.generar_hint_valido(total_unos=40) # 40 es menor que omega (55)
        
        y_bytes = hint_bit_pack(h_original, self.omega, self.k)
        
        # El tamaño final de la firma debe ser exactamente omega + k
        self.assertEqual(len(y_bytes), self.omega + self.k)
        
        h_recuperado = hint_bit_unpack(y_bytes, self.omega, self.k)
        self.assertEqual(h_original, h_recuperado, "Fallo en la reconstrucción del Hint")

    def test_hint_bit_unpack_malformed_order(self):
        """Ataque: Los índices dentro de un mismo polinomio no están en orden ascendente."""
        # Creamos una cadena de bytes vacía de tamaño omega + k
        y = bytearray(self.omega + self.k)
        
        # Simulamos que el polinomio 0 tiene dos 'unos' en las posiciones 10 y 5 (desordenados)
        y[0] = 10
        y[1] = 5
        y[self.omega] = 2 # El marcador indica que el polinomio 0 usa los primeros 2 índices
        
        resultado = hint_bit_unpack(bytes(y), self.omega, self.k)
        self.assertIsNone(resultado, "El sistema aceptó una firma con índices desordenados")

    def test_hint_bit_unpack_malformed_leftovers(self):
        """Ataque: Hay 'basura' en el espacio libre de omega."""
        y = bytearray(self.omega + self.k)
        
        # El vector está vacío (todos los marcadores a 0), pero inyectamos basura al final de omega
        y[self.omega - 1] = 255 
        
        resultado = hint_bit_unpack(bytes(y), self.omega, self.k)
        self.assertIsNone(resultado, "El sistema aceptó basura en los bytes sobrantes de omega")

    def test_w1_encode(self):
        """Verifica la compresión de w1 a bytes."""
        # Calculamos la cota b
        b = (Q - 1) // (2 * self.gamma2) - 1
        
        # Creamos un vector w1 simulado con coeficientes entre 0 y b
        w1 = [[random.randint(0, b) for _ in range(256)] for _ in range(self.k)]
        
        w1_bytes = w1_encode(w1, self.gamma2)
        
        # Verificamos la longitud teórica. Para ML-DSA-65, b=15 -> bitlen(15)=4
        # Longitud = 32 * k * bitlen(b) = 32 * 6 * 4 = 768 bytes
        c = b.bit_length()
        longitud_esperada = 32 * self.k * c
        
        self.assertEqual(len(w1_bytes), longitud_esperada)

if __name__ == '__main__':
    unittest.main()