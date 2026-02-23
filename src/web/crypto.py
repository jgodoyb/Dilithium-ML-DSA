"""
Funciones criptográficas asimétricas y de hash, enfocadas en encriptación y validación local de contraseñas.
"""
import base64
import hashlib
import re

from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

_ITERACIONES_PBKDF2 = 260_000   # OWASP 2024
_LONGITUD_CLAVE_PBKDF2 = 32

def derivar_clave_fernet(secreto: str, sal: bytes) -> bytes:
    """Deriva clave Fernet de 32 B (urlsafe-b64) mediante PBKDF2-SHA256."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=_LONGITUD_CLAVE_PBKDF2,
        salt=sal,
        iterations=_ITERACIONES_PBKDF2,
        backend=default_backend(),
    )
    return base64.urlsafe_b64encode(kdf.derive(secreto.encode("utf-8")))

def hashear_contrasena(contrasena: str, sal: bytes) -> str:
    return hashlib.sha256(contrasena.encode("utf-8") + sal).hexdigest()

def validar_contrasena(contra: str) -> list[str]:
    """
    Devuelve lista de errores. Lista vacía = contraseña válida.
    Requisitos: ≥8 chars, ≥1 mayúscula, ≥1 dígito.
    """
    errores = []
    if len(contra) < 8:
        errores.append("Mínimo 8 caracteres.")
    if not re.search(r"[A-Z]", contra):
        errores.append("Al menos una letra mayúscula.")
    if not re.search(r"\d", contra):
        errores.append("Al menos un número.")
    return errores
