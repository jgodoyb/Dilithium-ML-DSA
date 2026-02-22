# src/mldsa/ntt/operations.py
from mldsa.constants import Q

def add_ntt(a_hat: list, b_hat: list) -> list:
    """
    Algoritmo 44: AddNTT(a_hat, b_hat)
    Suma dos polinomios en el dominio NTT punto a punto.
    """
    c_hat = [0] * 256
    for i in range(256):
        c_hat[i] = (a_hat[i] + b_hat[i]) % Q
    return c_hat

def multiply_ntt(a_hat: list, b_hat: list) -> list:
    """
    Algoritmo 45: MultiplyNTT(a_hat, b_hat)
    Multiplica dos polinomios en el dominio NTT punto a punto.
    """
    c_hat = [0] * 256
    for i in range(256):
        c_hat[i] = (a_hat[i] * b_hat[i]) % Q
    return c_hat

def add_vector_ntt(v_hat: list, w_hat: list) -> list:
    """
    Algoritmo 46: AddVectorNTT(v_hat, w_hat)
    Suma dos vectores de polinomios de longitud l.
    """
    l = len(v_hat)
    u_hat = [None] * l
    for i in range(l):
        u_hat[i] = add_ntt(v_hat[i], w_hat[i])
    return u_hat

def scalar_vector_ntt(c_hat: list, v_hat: list) -> list:
    """
    Algoritmo 47: ScalarVectorNTT(c_hat, v_hat)
    Multiplica un polinomio escalar por un vector de polinomios.
    """
    l = len(v_hat)
    w_hat = [None] * l
    for i in range(l):
        w_hat[i] = multiply_ntt(c_hat, v_hat[i])
    return w_hat

def matrix_vector_ntt(M_hat: list, v_hat: list) -> list:
    """
    Algoritmo 48: MatrixVectorNTT(M_hat, v_hat)
    Multiplica una matriz de polinomios (k x l) por un vector de polinomios (l).
    Devuelve un vector de polinomios de longitud k.
    """
    k = len(M_hat)
    l = len(v_hat)
    
    # Inicializamos w_hat como un vector de k polinomios llenos de ceros
    w_hat = [[0] * 256 for _ in range(k)]
    
    for i in range(k):
        for j in range(l):
            # Multiplicamos la celda de la matriz por el elemento del vector
            producto = multiply_ntt(M_hat[i][j], v_hat[j])
            # Sumamos al acumulador de esa fila
            w_hat[i] = add_ntt(w_hat[i], producto)
            
    return w_hat