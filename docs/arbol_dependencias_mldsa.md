# Árbol de Dependencias del Código (ML-DSA / FIPS 204)

Este documento describe la arquitectura de dependencias de la biblioteca, organizada por niveles desde las funciones primitivas de más bajo nivel hasta la API pública expuesta. Cada nivel indica las dependencias matemáticas y los algoritmos correspondientes del estándar **FIPS 204**.

---

## 🔝 Resumen del Árbol de Dependencias

```
[Nivel 11: API Pública (ML-DSA / HashML-DSA)]
       │
[Nivel 10: Algoritmos Internos Principales (KeyGen, Sign, Verify internal)]
       ├─────────────────────────────────────────┐
[Nivel 9: Codificación de Claves/Firmas]   [Nivel 6: Funciones de Expansión]
       ├──────────────────────┐                  ├──────────────────────┐
[Nivel 8: Codif. Compleja] [Nivel 7: Descomp.] [Nivel 5: Muestreo]  [Nivel 4: Vectores NTT]
       │                      │                  │                      │
[Nivel 2: Empaquetado]        │                  ├──────────────────────┘
       ├──────────────────────┴──────────────────┤
[Nivel 1: Conversiones Básicas]            [Nivel 3: NTT y Aritmética T_q]
       │                                         │
[Nivel 0: Funciones Primitivas] ─────────────────┘
```

---

## Detalles por Niveles de Abstracción

### NIVEL 0: Funciones Primitivas (SIN dependencias)
*   `IntegerToBits` (Algoritmo 9)
*   `BitsToInteger` (Algoritmo 10)
*   `IntegerToBytes` (Algoritmo 11)
*   `BitRev8` (Algoritmo 43)

---

### NIVEL 1: Conversiones Básicas
*   `BitsToBytes` (Algoritmo 12)
    *   *Usa:* `IntegerToBits`
*   `BytesToBits` (Algoritmo 13)
    *   *Usa:* Ninguna (operación de manipulación directa a nivel de bits).
*   `CoeffFromThreeBytes` (Algoritmo 14)
    *   *Usa:* Operaciones aritméticas básicas.
*   `CoeffFromHalfByte` (Algoritmo 15)
    *   *Usa:* Operaciones aritméticas básicas.

---

### NIVEL 2: Empaquetado / Desempaquetado Simple
*   `SimpleBitPack` (Algoritmo 16)
    *   *Usa:* `IntegerToBits`, `BitsToBytes`
*   `SimpleBitUnpack` (Algoritmo 18)
    *   *Usa:* `BytesToBits`, `BitsToInteger`
*   `BitPack` (Algoritmo 17)
    *   *Usa:* `IntegerToBits`, `BitsToBytes`
*   `BitUnpack` (Algoritmo 19)
    *   *Usa:* `BytesToBits`, `BitsToInteger`

---

### NIVEL 3: NTT y Operaciones en $T_q$
*   `NTT` (Algoritmo 41)
    *   *Usa:* `BitRev8`, array precomputado de constantes de raíces de la unidad `zetas[]`.
    *   *Optimización:* Montgomery Reduction.
*   `NTT⁻¹` (Algoritmo 42)
    *   *Usa:* `BitRev8`, array precomputado de constantes de raíces de la unidad `zetas[]`.
    *   *Optimización:* Montgomery Reduction.
*   `AddNTT` (Algoritmo 44)
    *   *Usa:* Operaciones modulares básicas en anillo.
*   `MultiplyNTT` (Algoritmo 45)
    *   *Usa:* Operaciones modulares básicas en anillo.

---

### NIVEL 4: Operaciones Vectoriales NTT
*   `AddVectorNTT` (Algoritmo 46)
    *   *Usa:* `AddNTT`
*   `ScalarVectorNTT` (Algoritmo 47)
    *   *Usa:* `MultiplyNTT`
*   `MatrixVectorNTT` (Algoritmo 48)
    *   *Usa:* `AddNTT`, `MultiplyNTT`

---

### NIVEL 5: Funciones de Muestreo (Sampling)
*   `RejNTTPoly` (Algoritmo 30)
    *   *Usa:* SHAKE-128 (G), `CoeffFromThreeBytes`
    *   *Produce:* Elemento de $T_q$ (polinomio uniforme).
*   `RejBoundedPoly` (Algoritmo 31)
    *   *Usa:* SHAKE-256 (H), `CoeffFromHalfByte`
    *   *Produce:* Polinomio con coeficientes en el rango $[-\eta, \eta]$.
*   `SampleInBall` (Algoritmo 29)
    *   *Usa:* SHAKE-256 (H), `BytesToBits`
    *   *Produce:* Polinomio con $\tau$ coeficientes con valores $\pm 1$.
*   `ExpandMask` (Algoritmo 34)
    *   *Usa:* SHAKE-256 (H), `IntegerToBytes`, `BitUnpack`
    *   *Produce:* Vector $\mathbf{y}$ de polinomios.

---

### NIVEL 6: Funciones de Expansión
*   `ExpandA` (Algoritmo 32)
    *   *Usa:* `RejNTTPoly`, `IntegerToBytes`
    *   *Produce:* Matriz $\mathbf{\hat{A}}$ en representación NTT.
*   `ExpandS` (Algoritmo 33)
    *   *Usa:* `RejBoundedPoly`, `IntegerToBytes`
    *   *Produce:* Vectores secretos $\mathbf{s}_1, \mathbf{s}_2$.
*   *Nota:* `ExpandMask` (ya listado en el *Nivel 5*) también actúa como función de expansión en este nivel.

---

### NIVEL 7: Funciones de Descomposición
*   `Power2Round` (Algoritmo 35)
    *   *Usa:* Operaciones aritméticas y modulares elementales.
*   `Decompose` (Algoritmo 36)
    *   *Usa:* Operaciones modulares.
*   `HighBits` (Algoritmo 37)
    *   *Usa:* `Decompose`
*   `LowBits` (Algoritmo 38)
    *   *Usa:* `Decompose`
*   `MakeHint` (Algoritmo 39)
    *   *Usa:* `HighBits`
*   `UseHint` (Algoritmo 40)
    *   *Usa:* `Decompose`

---

### NIVEL 8: Codificación de Estructuras Complejas
*   `HintBitPack` (Algoritmo 20)
    *   *Usa:* Operaciones vectoriales para codificación binaria eficiente de pistas.
*   `HintBitUnpack` (Algoritmo 21)
    *   *Usa:* Operaciones y validaciones de límites sobre el vector desempaquetado.
*   `w1Encode` (Algoritmo 28)
    *   *Usa:* `SimpleBitPack`

---

### NIVEL 9: Codificación de Claves y Firmas
*   `pkEncode` (Algoritmo 22)
    *   *Usa:* `SimpleBitPack`
*   `pkDecode` (Algoritmo 23)
    *   *Usa:* `SimpleBitUnpack`
*   `skEncode` (Algoritmo 24)
    *   *Usa:* `BitPack`
*   `skDecode` (Algoritmo 25)
    *   *Usa:* `BitUnpack`
*   `sigEncode` (Algoritmo 26)
    *   *Usa:* `BitPack`, `HintBitPack`
*   `sigDecode` (Algoritmo 27)
    *   *Usa:* `BitUnpack`, `HintBitUnpack`

---

### NIVEL 10: Algoritmos Internos Principales
*   `ML-DSA.KeyGen_internal` (Algoritmo 6)
    *   *Usa:* SHAKE-256 (H), `IntegerToBytes`, `ExpandA`, `ExpandS`, `NTT`, `NTT⁻¹`, `MatrixVectorNTT`, `Power2Round`, `pkEncode`, `skEncode`.
    *   *Produce:* Clave pública ($pk$) y clave privada ($sk$).
*   `ML-DSA.Sign_internal` (Algoritmo 7)
    *   *Usa:* `skDecode`, SHAKE-256 (H), `IntegerToBytes`, `NTT`, `NTT⁻¹`, `ExpandA`, `ExpandMask`, `MatrixVectorNTT`, `ScalarVectorNTT`, `HighBits`, `LowBits`, `w1Encode`, `SampleInBall`, `MakeHint`, `sigEncode`.
    *   *Produce:* Firma digital $\sigma$.
*   `ML-DSA.Verify_internal` (Algoritmo 8)
    *   *Usa:* `pkDecode`, `sigDecode`, SHAKE-256 (H), `ExpandA`, `SampleInBall`, `NTT`, `NTT⁻¹`, `MatrixVectorNTT`, `UseHint`, `w1Encode`.
    *   *Produce:* Valor booleano de éxito/fallo.

---

### NIVEL 11: Algoritmos Externos (API Pública)
*   `ML-DSA.KeyGen` (Algoritmo 1)
    *   *Usa:* RBG (Random Bit Generator de `os.urandom`), `ML-DSA.KeyGen_internal`.
    *   *Produce:* Clave pública ($pk$) y clave privada ($sk$).
*   `ML-DSA.Sign` (Algoritmo 2)
    *   *Usa:* RBG, `IntegerToBytes`, `BytesToBits`, `ML-DSA.Sign_internal`.
    *   *Produce:* Firma digital $\sigma$.
*   `ML-DSA.Verify` (Algoritmo 3)
    *   *Usa:* `IntegerToBytes`, `BytesToBits`, `ML-DSA.Verify_internal`.
    *   *Produce:* Valor booleano de verificación.
*   `HashML-DSA.Sign` (Algoritmo 4)
    *   *Usa:* RBG, función Hash configurada (SHA-256, SHA-512 o SHAKE-128), `IntegerToBytes`, `BytesToBits`, `ML-DSA.Sign_internal`.
    *   *Produce:* Firma digital de pre-hash $\sigma$.
*   `HashML-DSA.Verify` (Algoritmo 5)
    *   *Usa:* Función Hash configurada, `IntegerToBytes`, `BytesToBits`, `ML-DSA.Verify_internal`.
    *   *Produce:* Valor booleano de verificación.
