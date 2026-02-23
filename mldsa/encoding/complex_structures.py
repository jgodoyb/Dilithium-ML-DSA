# src/mldsa/encoding/complex_structures.py
from mldsa.constants import Q
from mldsa.encoding.bitpacking import simple_bit_pack

def hint_bit_pack(h: list, omega: int, k: int) -> bytes:
    """
    Algoritmo 20: HintBitPack(h)
    Codifica un vector de polinomios h con coeficientes binarios en una cadena de bytes.
    Solo almacena las posiciones (índices) de los coeficientes distintos de cero.
    """
    # 1: y <- 0^(omega + k)
    y = bytearray(omega + k)
    index = 0
    
    # 3: for i from 0 to k - 1
    for i in range(k):
        for j in range(256):
            if h[i][j] != 0:
                y[index] = j
                index += 1
        # 10: Guardamos hasta dónde hemos llegado en este polinomio
        y[omega + i] = index
        
    return bytes(y)

def hint_bit_unpack(y: bytes, omega: int, k: int):
    """
    Algoritmo 21: HintBitUnpack(y)
    Revierte el HintBitPack. Devuelve el vector de polinomios o None si es inválido.
    """
    # 1: Inicializamos h como un vector de k polinomios llenos de ceros
    h = [[0] * 256 for _ in range(k)]
    index = 0
    
    for i in range(k):
        limite_actual = y[omega + i]
        
        # 4: Validación de seguridad
        if limite_actual < index or limite_actual > omega:
            return None # Malformed input
            
        first = index
        while index < limite_actual:
            if index > first:
                # 9: Los índices deben estar estrictamente en orden ascendente
                if y[index - 1] >= y[index]:
                    return None # Malformed input
                    
            # 12: Reconstruimos el 1 en la posición indicada
            h[i][y[index]] = 1
            index += 1
            
    # 16: Comprobamos que el resto de bytes no usados sean cero
    for i in range(index, omega):
        if y[i] != 0:
            return None # Malformed input
            
    return h

def w1_encode(w1: list, gamma2: int) -> bytes:
    """
    Algoritmo 28: w1Encode(w1)
    Codifica el vector polinómico w1 en una cadena de bytes.
    """
    w1_tilde = bytearray()
    
    # Límite superior de los coeficientes según FIPS 204
    b = (Q - 1) // (2 * gamma2) - 1
    k = len(w1)
    
    # 2: for i from 0 to k - 1
    for i in range(k):
        # 3: w1_tilde <- w1_tilde || SimpleBitPack(w1[i], b)
        w1_tilde.extend(simple_bit_pack(w1[i], b))
        
    return bytes(w1_tilde)