"""
Formato y manipulación de archivos de firma (.sig).
"""
import base64
import datetime
import textwrap
from typing import Optional

_INICIO_FIRMA = "-----BEGIN ML-DSA SIGNATURE-----"
_FIN_FIRMA    = "-----END ML-DSA SIGNATURE-----"
_VERSION_FIRMA = "2"
_ALGORITMO_PH  = "SHA-256"
_CONTEXTO      = b"Q-Proof"

def construir_archivo_firma(firma_binaria: bytes, firmante: str, nombre_archivo: str) -> str:
    ahora_utc = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    cuerpo_b64 = base64.b64encode(firma_binaria).decode("ascii")
    envuelto   = "\n".join(textwrap.wrap(cuerpo_b64, width=64))
    return (
        f"{_INICIO_FIRMA}\n"
        f"Version: {_VERSION_FIRMA}\n"
        f"Algorithm: HashML-DSA / {_ALGORITMO_PH}\n"
        f"Signer: {firmante}\n"
        f"File: {nombre_archivo}\n"
        f"Timestamp: {ahora_utc}\n"
        f"\n"
        f"{envuelto}\n"
        f"{_FIN_FIRMA}\n"
    )

def analizar_archivo_firma(texto_firma: str) -> Optional[bytes]:
    try:
        inicio     = texto_firma.index(_INICIO_FIRMA) + len(_INICIO_FIRMA)
        fin        = texto_firma.index(_FIN_FIRMA)
        bloque     = texto_firma[inicio:fin]
        cuerpo_b64 = bloque.split("\n\n", 1)[1] if "\n\n" in bloque else bloque
        return base64.b64decode("".join(cuerpo_b64.split()))
    except Exception:
        return None
