# Árbol de Dependencias de ML-DSA
Este documento mapea el orden cronológico de creación de archivos y las dependencias entre funciones.

## Nivel 1
**Creación del archivo `constants.py`**


## Nivel 2
**Creación del archivo `registry.py`**

- def get_parameters() -> dict:

## Nivel 3
**Creación del archivo `conversions.py`**

- def integer_to_bits() -> list: - Algoritmo 9: IntegerToBits(x, alpha).
- def bits_to_integer() -> int: - Algoritmo 10: BitsToInteger(y).
- def integer_to_bytes() -> bytes: - Algoritmo 11: IntegerToBytes(x, alpha).
- def bits_to_bytes() -> bytes: - Algoritmo 12: BitsToBytes(y).
- def bytes_to_bits() -> list: - Algoritmo 13: BytesToBits(z).
- def bit_rev_8() -> int: - Algoritmo 43: BitRev8(m).
    - def integer_to_bits(...)
    - def bits_to_integer(...)

## Nivel 4
**Creación del archivo `sampling.py`**

- def coeff_from_three_bytes(): - Algoritmo 14: CoeffFromThreeBytes(b0, b1, b2).
- def coeff_from_half_byte(): - Algoritmo 15: CoeffFromHalfByte(b).

## Nivel 5
**Creación del archivo `bitpacking.py`**

- def bitlen() -> int:
- def simple_bit_pack() -> bytes: - Algoritmo 16: SimpleBitPack(w, b)
    - def bitlen(...)
    - def bits_to_bytes(...)
    - def integer_to_bits(...)
- def simple_bit_unpack() -> list: - Algoritmo 18: SimpleBitUnpack(v, b)
    - def bitlen(...)
    - def bytes_to_bits(...)
    - def bits_to_integer(...)
- def bit_pack() -> bytes: - Algoritmo 17: BitPack(w, a, b)
    - def bitlen(...)
    - def bits_to_bytes(...)
    - def integer_to_bits(...)
- def bit_unpack() -> list: - Algoritmo 19: BitUnpack(v, a, b)
    - def bitlen(...)
    - def bytes_to_bits(...)
    - def bits_to_integer(...)

## Nivel 6
**Creación del archivo `ntt.py`**

- def ntt() -> list: - Algoritmo 41: NTT(w)
- def ntt_inv() -> list: - Algoritmo 42: NTT^-1(w_hat)

## Nivel 7
**Creación del archivo `operations.py`**

- def add_ntt() -> list: - Algoritmo 44: AddNTT(a_hat, b_hat)
- def multiply_ntt() -> list: - Algoritmo 45: MultiplyNTT(a_hat, b_hat)
- def add_vector_ntt() -> list: - Algoritmo 46: AddVectorNTT(v_hat, w_hat)
    - def add_ntt(...)
- def scalar_vector_ntt() -> list: - Algoritmo 47: ScalarVectorNTT(c_hat, v_hat)
    - def multiply_ntt(...)
- def matrix_vector_ntt() -> list: - Algoritmo 48: MatrixVectorNTT(M_hat, v_hat)
    - def multiply_ntt(...)
    - def add_ntt(...)

## Nivel 8
**Creación del archivo `hash_functions.py`**


## Nivel 9
**Creación del archivo `samplers.py`**

- def sample_in_ball() -> list: - Algoritmo 29: SampleInBall(rho)
    - def Init(...)
    - def Absorb(...)
    - def Squeeze(...)
    - def bytes_to_bits(...)
- def rej_ntt_poly() -> list: - Algoritmo 30: RejNTTPoly(rho)
    - def Init(...)
    - def Absorb(...)
    - def Squeeze(...)
    - def coeff_from_three_bytes(...)
- def rej_bounded_poly() -> list: - Algoritmo 31: RejBoundedPoly(rho)
    - def Init(...)
    - def Absorb(...)
    - def Squeeze(...)
    - def coeff_from_half_byte(...)
- def expand_mask() -> list: - Algoritmo 34: ExpandMask(rho, mu)
    - def digest(...)
    - def bit_unpack(...)
    - def integer_to_bytes(...)

## Nivel 10
**Creación del archivo `expanders.py`**

- def expand_a() -> list: - Algoritmo 32: ExpandA(rho)
    - def rej_ntt_poly(...)
    - def integer_to_bytes(...)
- def expand_s() -> tuple: - Algoritmo 33: ExpandS(rho')
    - def rej_bounded_poly(...)
    - def integer_to_bytes(...)

## Nivel 11
**Creación del archivo `rounding.py`**

- def mod_centered() -> int:
- def power2round(): - Algoritmo 35: Power2Round(r)
    - def mod_centered(...)
- def decompose(): - Algoritmo 36: Decompose(r)
    - def mod_centered(...)
- def highbits(): - Algoritmo 37: HighBits(r)
    - def decompose(...)
- def lowbits(): - Algoritmo 38: LowBits(r)
    - def decompose(...)
- def make_hint(): - Algoritmo 39: MakeHint(z, r)
    - def highbits(...)
- def use_hint(): - Algoritmo 40: UseHint(h, r)
    - def decompose(...)

## Nivel 12
**Creación del archivo `complex_structures.py`**

- def hint_bit_pack() -> bytes: - Algoritmo 20: HintBitPack(h)
- def hint_bit_unpack(): - Algoritmo 21: HintBitUnpack(y)
- def w1_encode() -> bytes: - Algoritmo 28: w1Encode(w1)
    - def simple_bit_pack(...)

## Nivel 13
**Creación del archivo `serialization.py`**

- def bitlen() -> int:
- def pk_encode() -> bytes: - Algoritmo 22: pkEncode. Empaqueta la clave pública.
    - def simple_bit_pack(...)
    - def bitlen(...)
- def pk_decode() -> tuple: - Algoritmo 23: pkDecode. Recupera rho y t1.
    - def bitlen(...)
    - def simple_bit_unpack(...)
- def sk_encode() -> bytes: - Algoritmo 24: skEncode. Empaqueta la clave privada.
    - def bit_pack(...)
- def sk_decode() -> tuple: - Algoritmo 25: skDecode. Recupera rho, K, tr, s1, s2, t0.
    - def bitlen(...)
    - def bit_unpack(...)
- def sig_encode() -> bytes: - Algoritmo 26: sigEncode. Empaqueta la firma.
    - def hint_bit_pack(...)
    - def bit_pack(...)
- def sig_decode() -> tuple: - Algoritmo 27: sigDecode. Recupera c_tilde, z, h.
    - def hint_bit_unpack(...)
    - def bitlen(...)
    - def bit_unpack(...)

## Nivel 14
**Creación del archivo `mldsa_internal.py`**

- def _inf_norm() -> int:
- def keygen_internal() -> tuple[bytes, bytes]:
    - def get_parameters(...)
    - def digest(...)
    - def expand_a(...)
    - def expand_s(...)
    - def matrix_vector_ntt(...)
    - def power2round(...)
    - def pk_encode(...)
    - def sk_encode(...)
    - def integer_to_bytes(...)
    - def ntt(...)
    - def ntt_inv(...)
- def sign_internal() -> bytes:
    - def get_parameters(...)
    - def sk_decode(...)
    - def expand_a(...)
    - def digest(...)
    - def ntt(...)
    - def expand_mask(...)
    - def matrix_vector_ntt(...)
    - def highbits(...)
    - def sample_in_ball(...)
    - def scalar_vector_ntt(...)
    - def lowbits(...)
    - def make_hint(...)
    - def sig_encode(...)
    - def ntt_inv(...)
    - def w1_encode(...)
    - def _inf_norm(...)
- def verify_internal() -> bool:
    - def get_parameters(...)
    - def pk_decode(...)
    - def sig_decode(...)
    - def expand_a(...)
    - def digest(...)
    - def sample_in_ball(...)
    - def ntt(...)
    - def matrix_vector_ntt(...)
    - def scalar_vector_ntt(...)
    - def use_hint(...)
    - def _inf_norm(...)
    - def ntt_inv(...)
    - def w1_encode(...)

## Nivel 15
**Creación del archivo `mldsa.py`**

- def _int_to_byte() -> bytes:
- def keygen() -> tuple[bytes, bytes]:
    - def keygen_internal(...)
- def sign() -> bytes:
    - def sign_internal(...)
    - def _int_to_byte(...)
- def verify() -> bool:
    - def verify_internal(...)
    - def _int_to_byte(...)
- def hash_sign() -> bytes:
    - def sign_internal(...)
    - def digest(...)
    - def _int_to_byte(...)
- def hash_verify() -> bool:
    - def verify_internal(...)
    - def digest(...)
    - def _int_to_byte(...)
