"""
ML-DSA Parameter definitions based on FIPS 204 Standard.
Includes standard and HashML-DSA parameter sets.
"""

ML_DSA_PARAMS = {
    "ML_DSA_44": {
        "d": 13,
        "tau": 39,
        "gamma_1": 131072,  # 2^17
        "gamma_2": 95232,   # (q-1)/88
        "k": 4,
        "l": 4,
        "eta": 2,
        "omega": 80,
        "c_tilde_bytes": 32,
        "oid": (2, 16, 840, 1, 101, 3, 4, 3, 17),
    },
    "ML_DSA_65": {
        "d": 13,
        "tau": 49,
        "gamma_1": 524288,  # 2^19
        "gamma_2": 261888,  # (q-1)/32
        "k": 6,
        "l": 5,
        "eta": 4,
        "omega": 55,
        "c_tilde_bytes": 48,
        "oid": (2, 16, 840, 1, 101, 3, 4, 3, 18),
    },
    "ML_DSA_87": {
        "d": 13,
        "tau": 60,
        "gamma_1": 524288,  # 2^19
        "gamma_2": 261888,  # (q-1)/32
        "k": 8,
        "l": 7,
        "eta": 2,
        "omega": 75,
        "c_tilde_bytes": 64,
        "oid": (2, 16, 840, 1, 101, 3, 4, 3, 19),
    },
    "HASH_ML_DSA_44_WITH_SHA512": {
        "d": 13,
        "tau": 39,
        "gamma_1": 131072,  # 2^17
        "gamma_2": 95232,   # (q-1)/88
        "k": 4,
        "l": 4,
        "eta": 2,
        "omega": 80,
        "c_tilde_bytes": 32,
        "oid": (2, 16, 840, 1, 101, 3, 4, 3, 32),
    },
    "HASH_ML_DSA_65_WITH_SHA512": {
        "d": 13,
        "tau": 49,
        "gamma_1": 524288,  # 2^19
        "gamma_2": 261888,  # (q-1)/32
        "k": 6,
        "l": 5,
        "eta": 4,
        "omega": 55,
        "c_tilde_bytes": 48,
        "oid": (2, 16, 840, 1, 101, 3, 4, 3, 33),
    },
    "HASH_ML_DSA_87_WITH_SHA512": {
        "d": 13,
        "tau": 60,
        "gamma_1": 524288,  # 2^19
        "gamma_2": 261888,  # (q-1)/32
        "k": 8,
        "l": 7,
        "eta": 2,
        "omega": 75,
        "c_tilde_bytes": 64,
        "oid": (2, 16, 840, 1, 101, 3, 4, 3, 34),
    },
}

def get_parameters(level: str) -> dict:
    """Returns the parameter dictionary for the specified security level.
    Defaults to ML_DSA_65 if unknown."""
    return ML_DSA_PARAMS.get(level.upper(), ML_DSA_PARAMS["ML_DSA_65"])
