# Dilithium-ML-DSA (FIPS 204 Cryptographic Core)

Este repositorio contiene una implementación limpia y modular en Python del estándar **ML-DSA (FIPS 204)**, el algoritmo de firma digital post-cuántica seleccionado por el NIST. 

La biblioteca ha sido desarrollada **desde cero y posee cero dependencias externas**, utilizando únicamente los módulos provistos por la biblioteca estándar de Python (como `hashlib` y `os.urandom`), lo que garantiza la ausencia de vulnerabilidades de cadena de suministro y facilita su auditoría.

---

## ✨ Características Principales

*   **Algoritmo Post-Cuántico Puro:** Implementación nativa basada en retículos estructurados del algoritmo de firma digital ML-DSA bajo el estándar oficial FIPS 204.
*   **Parámetros Oficiales Integrados:** Soporte completo de los conjuntos de parámetros estándar definidos en el FIPS 204:
    *   **ML-DSA-44** (Nivel de seguridad 2)
    *   **ML-DSA-65** (Nivel de seguridad 3, por defecto)
    *   **ML-DSA-87** (Nivel de seguridad 5)
*   **Modos Soportados:**
    *   **ML-DSA (Puro):** Firma directa del mensaje con separación de dominio.
    *   **HashML-DSA (Pre-Hash):** Firma de resúmenes de mensajes para optimizar el rendimiento con grandes volúmenes de datos. Soporta **SHA-256**, **SHA-512** y **SHAKE128** (256 bits).
*   **Separación de Dominios (Contexto):** Soporte estricto de contextos (`ctx`) de hasta 255 bytes en la generación de firmas, proporcionando una sólida protección contra ataques de colisión y confusión de dominio entre aplicaciones.
*   **Cero Dependencias de Terceros:** Corre de forma autónoma en cualquier entorno de Python 3.10 o superior sin necesidad de instalar librerías externas.

---

## 📁 Estructura de Módulos

El código criptográfico está estructurado de forma modular y pedagógica según los algoritmos detallados en la especificación FIPS 204:

*   `mldsa/`:
    *   `mldsa.py`: Interfaz principal pública (expone `keygen`, `sign`, `verify`, `hash_sign`, `hash_verify`).
    *   `constants.py`: Constantes universales del anillo y del módulo (Q = 8380417, N = 256).
    *   `parameters/`: Diccionario de parámetros oficiales (k, l, eta, gamma1, gamma2, etc.) y selector de nivel de seguridad.
    *   `core/`: Implementación de algoritmos de bajo nivel (`keygen_internal`, `sign_internal`, `verify_internal`).
    *   `crypto/`: Funciones hash auxiliares basadas en SHAKE-128 y SHAKE-256 (según FIPS 202).
    *   `decomposition/`: Operaciones de redondeo y descomposición de coeficientes (`Power2Round`, `Decompose`, `HighBits`, `LowBits`, `MakeHint`, `UseHint`).
    *   `encoding/`: Codificación y empaquetado de bits (`BitPack`, `BitUnpack`, empaquetado de pistas/hints y serialización de firmas y claves).
    *   `ntt/`: Aritmética polinomial rápida basada en la Transformación Teórica de Números (NTT).
    *   `primitives/`: Conversiones básicas de tipos (Integer a Bytes, Bits a Bytes, etc.).
    *   `sampling/`: Algoritmos de muestreo determinista y rechazo (`SampleInBall`, `RejNTTPoly`, `RejBoundedPoly`, `ExpandMask`, `ExpandA`, `ExpandS`).
    *   `arbol_dependencias_mldsa.md`: Documento técnico detallado que mapea las funciones, su nivel de dependencia matemática y su relación con los algoritmos del estándar.
*   `tests/`: Amplia suite de pruebas unitarias que validan la correctitud aritmética y lógica de cada sección (NTT, empaquetado, redondeo, muestreo y API pública).

---

## 🚀 Instalación y Uso

### 1. Requisitos
*   **Python 3.10** o superior instalado.
*   No requiere ningún paso de compilación ni instalación de dependencias externas.

### 2. Uso Básico (Ejemplo)

```python
import base64
from mldsa import keygen, sign, verify, hash_sign, hash_verify

# 1. Generación de claves (Nivel por defecto: ML-DSA-65)
public_key, private_key = keygen()

mensaje = b"Mensaje confidencial para firma digital"
contexto = b"Contexto de la aplicacion"

# --- Variante Pura ---
# Generar Firma
firma = sign(private_key, mensaje, ctx=contexto)

# Verificar Firma
valido = verify(public_key, mensaje, firma, ctx=contexto)
print(f"Verificación Firma Pura: {valido}")  # True

# --- Variante Pre-Hash (HashML-DSA con SHA-256) ---
firma_hash = hash_sign(private_key, mensaje, ph_algo="SHA-256", ctx=contexto)
valido_hash = hash_verify(public_key, mensaje, firma_hash, ph_algo="SHA-256", ctx=contexto)
print(f"Verificación Firma Pre-Hash: {valido_hash}")  # True
```

---

## 🧪 Pruebas Unitarias

Para ejecutar el set completo de pruebas unitarias y verificar la correctitud de todos los componentes del núcleo criptográfico:

```bash
python -m unittest discover -s tests -p "*.py"
```

---

## 📄 Licencia

Este proyecto está diseñado con fines de investigación académica y estudio de la criptografía moderna post-cuántica.
