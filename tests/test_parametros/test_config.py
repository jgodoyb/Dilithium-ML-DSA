import unittest
import sys
import os

# Ajuste de path para que Python encuentre la carpeta 'mldsa' dentro de 'src'
# Desde src/tests/test_parametros subimos dos niveles para llegar a src/
ruta_raiz_codigo = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if ruta_raiz_codigo not in sys.path:
    sys.path.insert(0, ruta_raiz_codigo)

from mldsa.constants import Q, N
from mldsa.parameters.registry import get_parameters, ML_DSA_PARAMS

class TestConfiguracionMLDSA(unittest.TestCase):
    
    def test_constantes_universales(self):
        """Verifica que Q y N coinciden con el estándar FIPS 204"""
        self.assertEqual(Q, 8380417, "El módulo Q debe ser 8380417")
        self.assertEqual(N, 256, "El grado N debe ser 256")

    def test_diccionario_parametros_todos_niveles(self):
        """Verifica que el diccionario de parámetros existe y tiene propiedades lógicas"""
        for nivel in ["ML_DSA_44", "ML_DSA_65", "ML_DSA_87"]:
            with self.subTest(nivel=nivel):
                p = get_parameters(nivel)
                
                # Relaciones básicas del anillo
                self.assertIn("k", p)
                self.assertIn("l", p)
                self.assertIn("eta", p)
                self.assertIn("tau", p)
                self.assertIn("gamma_1", p)
                self.assertIn("gamma_2", p)
                self.assertIn("omega", p)
                self.assertIn("c_tilde_bytes", p)
                self.assertIn("oid", p)

if __name__ == '__main__':
    unittest.main()