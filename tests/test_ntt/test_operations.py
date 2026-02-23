# src/tests/test_ntt/test_operations.py
import unittest
import sys
import os
import random

ruta_raiz = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if ruta_raiz not in sys.path:
    sys.path.insert(0, ruta_raiz)

from mldsa.ntt.operations import (
    add_ntt, multiply_ntt,
    add_vector_ntt, scalar_vector_ntt, matrix_vector_ntt
)
from mldsa.constants import Q

class TestNTTOperations(unittest.TestCase):

    def generar_polinomio(self):
        return [random.randint(0, Q - 1) for _ in range(256)]

    def test_add_ntt_properties(self):
        """Verifica la conmutatividad y el elemento neutro de la suma"""
        a = self.generar_polinomio()
        b = self.generar_polinomio()
        ceros = [0] * 256
        
        # Conmutativa: a + b == b + a
        self.assertEqual(add_ntt(a, b), add_ntt(b, a))
        # Elemento neutro: a + 0 == a
        self.assertEqual(add_ntt(a, ceros), a)

    def test_multiply_ntt_properties(self):
        """Verifica la conmutatividad y el elemento neutro de la multiplicación"""
        a = self.generar_polinomio()
        b = self.generar_polinomio()
        unos = [1] * 256
        ceros = [0] * 256
        
        # Conmutativa: a * b == b * a
        self.assertEqual(multiply_ntt(a, b), multiply_ntt(b, a))
        # Elemento neutro: a * 1 == a
        self.assertEqual(multiply_ntt(a, unos), a)
        # Elemento absorbente: a * 0 == 0
        self.assertEqual(multiply_ntt(a, ceros), ceros)

    def test_vector_distributive_property(self):
        """Propiedad distributiva: c * (v + w) == (c * v) + (c * w)"""
        l = 3 # Longitud del vector
        c = self.generar_polinomio() # Escalar
        v = [self.generar_polinomio() for _ in range(l)]
        w = [self.generar_polinomio() for _ in range(l)]
        
        # 1. c * (v + w)
        v_plus_w = add_vector_ntt(v, w)
        resultado_izq = scalar_vector_ntt(c, v_plus_w)
        
        # 2. (c * v) + (c * w)
        cv = scalar_vector_ntt(c, v)
        cw = scalar_vector_ntt(c, w)
        resultado_der = add_vector_ntt(cv, cw)
        
        self.assertEqual(resultado_izq, resultado_der, "Fallo en propiedad distributiva vectorial")

    def test_matrix_vector_dimensions(self):
        """Verifica que MatrixVectorNTT devuelve las dimensiones correctas (k)"""
        k, l = 4, 3
        # Matriz M de dimensiones (k x l)
        M = [[self.generar_polinomio() for _ in range(l)] for _ in range(k)]
        # Vector v de longitud l
        v = [self.generar_polinomio() for _ in range(l)]
        
        # Multiplicamos
        resultado = matrix_vector_ntt(M, v)
        
        # El resultado debe ser un vector de longitud k
        self.assertEqual(len(resultado), k)
        # Cada elemento del vector debe ser un polinomio de 256 coeficientes
        for poli in resultado:
            self.assertEqual(len(poli), 256)

if __name__ == '__main__':
    unittest.main()