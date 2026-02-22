import unittest
import sys
import os

# El "puente" para que Python encuentre el paquete 'mldsa'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from mldsa.primitives.conversions import (
    integer_to_bits, bits_to_integer, 
    integer_to_bytes, bits_to_bytes, 
    bytes_to_bits, bit_rev_8
)

class TestPrimitivasMLDSA(unittest.TestCase):
    
    def test_alg_9_10_integer_bits(self):
        """Verifica la conversión entre Enteros y Bits (Algoritmos 9 y 10)"""
        # 13 en 4 bits es [1, 0, 1, 1] (LSB primero)
        bits = integer_to_bits(13, 4)
        self.assertEqual(bits, [1, 0, 1, 1])
        self.assertEqual(bits_to_integer(bits), 13)

    def test_alg_11_integer_bytes(self):
        """Verifica la conversión de Enteros a Bytes (Algoritmo 11)"""
        # 258 en 2 bytes es [2, 1] (2 + 1*256)
        self.assertEqual(integer_to_bytes(258, 2), b'\x02\x01')

    def test_alg_12_13_bits_bytes(self):
        """Verifica la conversión entre Bits y Bytes (Algoritmos 12 y 13)"""
        # El byte 1 (00000001)
        bits = [1, 0, 0, 0, 0, 0, 0, 0]
        self.assertEqual(bits_to_bytes(bits), b'\x01')
        self.assertEqual(bytes_to_bits(b'\x01'), bits)
        
    def test_round_trip_complex(self):
        """Prueba de integridad con una cadena de texto (como un PDF)"""
        original = b"Hola TFG"
        bits = bytes_to_bits(original)
        resultado = bits_to_bytes(bits)
        self.assertEqual(resultado, original)

    def test_bit_rev_8(self):
        """Verifica la reversión de bits (Algoritmo 11 auxiliar)"""
        # 1 (00000001) -> 128 (10000000)
        self.assertEqual(bit_rev_8(1), 128)

if __name__ == '__main__':
    unittest.main()