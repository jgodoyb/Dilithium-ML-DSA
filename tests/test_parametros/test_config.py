import unittest
import sys
import os

# Ajuste de path para que Python encuentre la carpeta 'mldsa' dentro de 'src'
# Desde src/tests/test_parametros subimos dos niveles para llegar a src/
ruta_raiz_codigo = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if ruta_raiz_codigo not in sys.path:
    sys.path.insert(0, ruta_raiz_codigo)

from mldsa.constants import Q, N
from mldsa.parameters.mldsa65 import ML_DSA_65

class TestConfiguracionMLDSA65(unittest.TestCase):
    
    def test_constantes_universales(self):
        """Verifica que Q y N coinciden con el estándar FIPS 204"""
        self.assertEqual(Q, 8380417, "El módulo Q debe ser 8380417")
        self.assertEqual(N, 256, "El grado N debe ser 256")

    def test_diccionario_parametros_nivel3(self):
        """Verifica que el diccionario ML_DSA_65 tiene los valores del NIST"""
        p = ML_DSA_65
        
        # Dimensiones y seguridad
        self.assertEqual(p["k"], 6, "K para Nivel 3 debe ser 6")
        self.assertEqual(p["l"], 5, "L para Nivel 3 debe ser 5")
        self.assertEqual(p["eta"], 4, "ETA para Nivel 3 debe ser 4")
        
        # Parámetros de firma
        self.assertEqual(p["tau"], 49, "TAU para Nivel 3 debe ser 49")
        self.assertEqual(p["gamma_1"], 524288, "GAMMA1 debe ser 2^19")
        self.assertEqual(p["gamma_2"], 261888, "GAMMA2 debe ser (Q-1)/32")
        
        # Identificación y Hash
        self.assertEqual(p["c_tilde_bytes"], 48, "C_TILDE_BYTES debe ser 48 para Nivel 3")
        self.assertEqual(p["oid"], (2, 16, 840, 1, 101, 3, 4, 3, 18), "OID incorrecto para Nivel 3")

if __name__ == '__main__':
    unittest.main()