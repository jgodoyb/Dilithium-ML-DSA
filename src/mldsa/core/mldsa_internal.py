# src/mldsa/core/mldsa_internal.py
from mldsa.crypto.hash_functions import H
from mldsa.primitives.conversions import integer_to_bytes
from mldsa.sampling.expanders import expand_a, expand_s
from mldsa.sampling.samplers import expand_mask, sample_in_ball
from mldsa.decomposition.rounding import power2round, highbits, lowbits, make_hint, use_hint
from mldsa.encoding.complex_structures import w1_encode
from mldsa.encoding.serialization import pk_encode, pk_decode, sk_encode, sk_decode, sig_encode, sig_decode
from mldsa.parameters.mldsa65 import ML_DSA_65
from mldsa.constants import Q, D

# Importaciones de TUS módulos de NTT
from mldsa.ntt.ntt import ntt, ntt_inv
from mldsa.ntt.operations import matrix_vector_ntt, scalar_vector_ntt

def _inf_norm(vector: list) -> int:
    """Función auxiliar para calcular ||v||_inf (Norma infinita)."""
    max_val = 0
    for poly in vector:
        for x in poly:
            val = x % Q
            if val > Q // 2: val -= Q
            if abs(val) > max_val: max_val = abs(val)
    return max_val

# =============================================================================
# ALGORITMO 6: ML-DSA.KeyGen_internal(xi)
# =============================================================================
def keygen_internal(xi: bytes) -> tuple[bytes, bytes]:
    # 0. Parámetros
    k, l, eta = ML_DSA_65["k"], ML_DSA_65["l"], ML_DSA_65["eta"]
    
    # 1: (rho, rho', K) <- H(xi || k || l, 128)
    seed_input = xi + integer_to_bytes(k, 1) + integer_to_bytes(l, 1)
    expanded_seed = H.digest(seed_input, 128)
    rho = expanded_seed[0:32]
    rho_prime = expanded_seed[32:96]
    K = expanded_seed[96:128]

    # 3: A_hat <- ExpandA(rho)
    A_hat = expand_a(rho, k, l)

    # 4: (s1, s2) <- ExpandS(rho')
    s1, s2 = expand_s(rho_prime, k, l, eta)

    # 5: t <- NTT^-1(A_hat * NTT(s1)) + s2
    s1_hat = [ntt(p) for p in s1]
    t_hat = matrix_vector_ntt(A_hat, s1_hat)
    t = []
    for i in range(k):
        # t = NTT^-1(t_hat) + s2
        poly_t = ntt_inv(t_hat[i])
        t.append([(poly_t[j] + s2[i][j]) % Q for j in range(256)])

    # 6: (t1, t0) <- Power2Round(t)
    t1, t0 = power2round(t, D)

    # 8: pk <- pkEncode(rho, t1)
    pk = pk_encode(rho, t1, D)

    # 9: tr <- H(pk, 64)
    tr = H.digest(pk, 64)

    # 10: sk <- skEncode(rho, K, tr, s1, s2, t0)
    sk = sk_encode(rho, K, tr, s1, s2, t0, eta, D)

    return pk, sk

# =============================================================================
# ALGORITMO 7: ML-DSA.Sign_internal(sk, M', rnd)
# =============================================================================
def sign_internal(sk: bytes, m_prime: bytes, rnd: bytes) -> bytes:
    # 0. Parámetros
    k, l = ML_DSA_65["k"], ML_DSA_65["l"]
    eta, tau = ML_DSA_65["eta"], ML_DSA_65["tau"]
    gamma1, gamma2 = ML_DSA_65["gamma_1"], ML_DSA_65["gamma_2"]
    omega = ML_DSA_65["omega"]
    c_tilde_len = ML_DSA_65["c_tilde_bytes"]
    beta = tau * eta

    # 1: (rho, K, tr, s1, s2, t0) <- skDecode(sk)
    rho, K, tr, s1, s2, t0 = sk_decode(sk, k, l, eta, D)

    # 2-4: NTT de los secretos
    s1_hat = [ntt(p) for p in s1]
    s2_hat = [ntt(p) for p in s2]
    t0_hat = [ntt(p) for p in t0]

    # 5: A_hat <- ExpandA(rho)
    A_hat = expand_a(rho, k, l)

    # 6: mu <- H(tr || M', 64)
    mu = H.digest(tr + m_prime, 64)

    # 7: rho'' <- H(K || rnd || mu, 64)
    rho_pp = H.digest(K + rnd + mu, 64)

    # 8-9: inicializar kappa y loop
    kappa = 0
    while True:
        # 11: y <- ExpandMask(rho'', kappa)
        y = expand_mask(rho_pp, kappa, l, gamma1)

        # 12: w <- NTT^-1(A_hat * NTT(y))
        y_hat = [ntt(p) for p in y]
        w_hat = matrix_vector_ntt(A_hat, y_hat)
        w = [ntt_inv(p_hat) for p_hat in w_hat]

        # 13: w1 <- HighBits(w)
        w1 = highbits(w, gamma2)

        # 15: c_tilde <- H(mu || w1Encode(w1), lambda/4)
        c_tilde = H.digest(mu + w1_encode(w1, gamma2), c_tilde_len)

        # 16: c <- SampleInBall(c_tilde)
        c = sample_in_ball(c_tilde, tau)
        c_hat = ntt(c)

        # 18: <<cs1>> <- NTT^-1(c_hat * s1_hat)
        cs1_hat = scalar_vector_ntt(c_hat, s1_hat)
        cs1 = [ntt_inv(p) for p in cs1_hat]

        # 19: <<cs2>> <- NTT^-1(c_hat * s2_hat)
        cs2_hat = scalar_vector_ntt(c_hat, s2_hat)
        cs2 = [ntt_inv(p) for p in cs2_hat]

        # 20: z <- y + <<cs1>>
        z = [[(y[i][j] + cs1[i][j]) % Q for j in range(256)] for i in range(l)]

        # 21: r0 <- LowBits(w - <<cs2>>)
        w_minus_cs2 = [[(w[i][j] - cs2[i][j]) % Q for j in range(256)] for i in range(k)]
        r0 = lowbits(w_minus_cs2, gamma2)

        # 23: if ||z||inf >= gamma1 - beta or ||r0||inf >= gamma2 - beta
        if _inf_norm(z) >= (gamma1 - beta) or _inf_norm(r0) >= (gamma2 - beta):
            kappa += l
            continue

        # 25: <<ct0>> <- NTT^-1(c_hat * t0_hat)
        ct0_hat = scalar_vector_ntt(c_hat, t0_hat)
        ct0 = [ntt_inv(p) for p in ct0_hat]

        # 26: h <- MakeHint(-<<ct0>>, w - <<cs2>> + <<ct0>>)
        minus_ct0 = [[(-x) % Q for x in p] for p in ct0]
        hint_in2 = [[(w_minus_cs2[i][j] + ct0[i][j]) % Q for j in range(256)] for i in range(k)]
        h = make_hint(minus_ct0, hint_in2, gamma2)

        # 28: if ||ct0||inf >= gamma2 or peso(h) > omega
        peso_h = sum(sum(1 for x in p if x != 0) for p in h)
        if _inf_norm(ct0) >= gamma2 or peso_h > omega:
            kappa += l
            continue

        # 33: sigma <- sigEncode(c_tilde, z, h)
        # Centramos z en [-Q/2, Q/2] como pide el estándar (mod+- q)
        z_cent = [[(x % Q if x % Q <= Q//2 else (x % Q) - Q) for x in p] for p in z]
        return sig_encode(c_tilde, z_cent, h, gamma1, omega, k)

# =============================================================================
# ALGORITMO 8: ML-DSA.Verify_internal(pk, M', sigma)
# =============================================================================
def verify_internal(pk: bytes, m_prime: bytes, sigma: bytes) -> bool:
    # 0. Parámetros
    k, l = ML_DSA_65["k"], ML_DSA_65["l"]
    tau, eta = ML_DSA_65["tau"], ML_DSA_65["eta"]
    gamma1, gamma2, omega = ML_DSA_65["gamma_1"], ML_DSA_65["gamma_2"], ML_DSA_65["omega"]
    c_tilde_len = ML_DSA_65["c_tilde_bytes"]
    beta = tau * eta

    # 1: (rho, t1) <- pkDecode(pk)
    decoded_pk = pk_decode(pk, k, D)
    if not decoded_pk: return False
    rho, t1 = decoded_pk

    # 2: (c_tilde, z, h) <- sigDecode(sigma)
    decoded_sig = sig_decode(sigma, l, gamma1, omega, k, c_tilde_len)
    if not decoded_sig: return False
    c_tilde, z, h = decoded_sig

    # 3-4: if h = perpendicular return false
    if h is None: return False

    # 5: A_hat <- ExpandA(rho)
    A_hat = expand_a(rho, k, l)

    # 6: tr <- H(pk, 64)
    tr = H.digest(pk, 64)

    # 7: mu <- H(tr || M', 64)
    mu = H.digest(tr + m_prime, 64)

    # 8: c <- SampleInBall(c_tilde)
    c = sample_in_ball(c_tilde, tau)
    c_hat = ntt(c)

    # 9: w' <- Az - c*t1*2^d
    z_hat = [ntt(p) for p in z]
    t1_2d_hat = [ntt([(coeff << D) % Q for coeff in poly]) for poly in t1]
    
    Az_hat = matrix_vector_ntt(A_hat, z_hat)
    ct1_hat = scalar_vector_ntt(c_hat, t1_2d_hat)
    
    # Inversa de (Az_hat - ct1_hat)
    w_approx = []
    for i in range(k):
        diff_hat = [(Az_hat[i][j] - ct1_hat[i][j]) % Q for j in range(256)]
        w_approx.append(ntt_inv(diff_hat))

    # 10: w1' <- UseHint(h, w')
    w1_prime = use_hint(h, w_approx, gamma2)

    # 12: c'_tilde <- H(mu || w1Encode(w1'))
    c_tilde_prime = H.digest(mu + w1_encode(w1_prime, gamma2), c_tilde_len)

    # 13: return ||z||inf < gamma1 - beta and c_tilde == c_tilde_prime
    z_is_short = _inf_norm(z) < (gamma1 - beta)
    hashes_match = (c_tilde == c_tilde_prime)

    return z_is_short and hashes_match