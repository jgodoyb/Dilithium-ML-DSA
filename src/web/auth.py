"""
Lógica para el manejo de sesiones de usuario y registro.
"""
import os
import re
import datetime
import base64
import random
from typing import Optional
from cryptography.fernet import Fernet, InvalidToken

import sqlite3
from .db import obtener_conexion
from .crypto import derivar_clave_fernet, hashear_contrasena, validar_contrasena
from .email_sender import enviar_correo_otp

# Agregamos mldsa path (asegurándonos de importar desde src folder)
import sys
_DIR_WEB = os.path.dirname(os.path.abspath(__file__))
_DIR_SRC = os.path.dirname(_DIR_WEB)
if _DIR_SRC not in sys.path:
    sys.path.insert(0, _DIR_SRC)

import mldsa

def registrar_usuario(
    usuario: str,
    correo: str,
    nombre_completo: str,
    fecha_nacimiento: str,
    contrasena: str,
) -> tuple[bool, str]:
    """
    Registra un nuevo usuario:
    · Valida todos los campos.
    · Genera par de claves ML-DSA.
    · Cifra la clave privada de dos formas:
        - Con la contraseña (acceso normal).
        - Con el e-mail (recuperación si se olvida la contraseña).
    """
    usuario  = usuario.strip()
    correo   = correo.strip().lower()
    nombre_completo = nombre_completo.strip()

    # ── Validaciones ──────────────────────────────────────────────────────
    if not all([usuario, correo, nombre_completo, fecha_nacimiento, contrasena]):
        return False, "Todos los campos son obligatorios."
    if len(usuario) < 3:
        return False, "El nombre de usuario debe tener al menos 3 caracteres."
    if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", correo):
        return False, "El formato del correo electrónico no es válido."

    errores_contrasena = validar_contrasena(contrasena)
    if errores_contrasena:
        return False, " ".join(errores_contrasena)

    with obtener_conexion() as conexion:
        if conexion.execute("SELECT 1 FROM usuarios WHERE usuario=?", (usuario,)).fetchone():
            return False, f"El usuario '{usuario}' ya está registrado."
        if conexion.execute("SELECT 1 FROM usuarios WHERE correo=?", (correo,)).fetchone():
            return False, "Ya existe una cuenta con ese correo."

        # ── Material criptográfico ─────────────────────────────────────────
        sal              = os.urandom(16)
        sal_correo       = os.urandom(16)

        fernet_contra    = Fernet(derivar_clave_fernet(contrasena, sal))
        fernet_correo    = Fernet(derivar_clave_fernet(correo, sal_correo))

        hash_contra      = hashear_contrasena(contrasena, sal)
        bytes_cp, bytes_cpr = mldsa.keygen()

        cp_b64           = base64.b64encode(bytes_cp).decode("ascii")
        cpr_enc_contra   = fernet_contra.encrypt(bytes_cpr)
        cpr_enc_correo   = fernet_correo.encrypt(bytes_cpr)

        conexion.execute(
            """INSERT INTO usuarios
               (usuario, correo, nombre_completo, fecha_nacimiento,
                hash_contrasena, sal, sal_correo,
                clave_publica_b64, clave_privada_enc, cpr_correo_enc)
               VALUES (?,?,?,?,?,?,?,?,?,?)""",
            (usuario, correo, nombre_completo, fecha_nacimiento,
             hash_contra, sal, sal_correo,
             cp_b64, cpr_enc_contra, cpr_enc_correo),
        )
        conexion.commit()

    return True, f"Cuenta creada con éxito para '{usuario}'."


def iniciar_sesion(usuario: str, contrasena: str) -> tuple[bool, Optional[bytes]]:
    """Verifica credenciales. Devuelve (True, clave_fernet) o (False, None)."""
    with obtener_conexion() as conexion:
        fila = conexion.execute(
            "SELECT hash_contrasena, sal FROM usuarios WHERE usuario=?",
            (usuario.strip(),),
        ).fetchone()
    if fila and hashear_contrasena(contrasena, fila["sal"]) == fila["hash_contrasena"]:
        return True, derivar_clave_fernet(contrasena, fila["sal"])
    return False, None


def obtener_clave_publica(usuario: str) -> Optional[bytes]:
    with obtener_conexion() as conexion:
        fila = conexion.execute(
            "SELECT clave_publica_b64 FROM usuarios WHERE usuario=?", (usuario,)
        ).fetchone()
    return base64.b64decode(fila["clave_publica_b64"]) if fila else None


def obtener_clave_privada(usuario: str, clave_fernet: bytes) -> Optional[bytes]:
    with obtener_conexion() as conexion:
        fila = conexion.execute(
            "SELECT clave_privada_enc FROM usuarios WHERE usuario=?", (usuario,)
        ).fetchone()
    if not fila:
        return None
    try:
        return Fernet(clave_fernet).decrypt(fila["clave_privada_enc"])
    except InvalidToken:
        return None


def obtener_usuario_por_correo(correo: str) -> Optional[sqlite3.Row]:
    """Devuelve la fila del usuario (o None) a partir de su correo."""
    with obtener_conexion() as conexion:
        return conexion.execute(
            "SELECT * FROM usuarios WHERE correo=?", (correo.strip().lower(),)
        ).fetchone()


def restablecer_contrasena_con_correo(
    correo: str, nueva_contrasena: str
) -> tuple[bool, str]:
    """
    Restablece la contraseña del usuario:
    1. Descifra la clave privada usando el correo (clave de recuperación).
    2. Re-cifra con la nueva contraseña.
    3. Actualiza hash_contrasena, sal, clave_privada_enc en la BD.
    La clave de respaldo (cpr_correo_enc) permanece intacta.
    """
    errores_contrasena = validar_contrasena(nueva_contrasena)
    if errores_contrasena:
        return False, " ".join(errores_contrasena)

    fila = obtener_usuario_por_correo(correo)
    if not fila:
        return False, "No existe ninguna cuenta con ese correo."

    # Descifrar CPR usando la clave derivada del correo
    fernet_correo = Fernet(derivar_clave_fernet(correo.strip().lower(), fila["sal_correo"]))
    try:
        bytes_cpr = fernet_correo.decrypt(fila["cpr_correo_enc"])
    except InvalidToken:
        return False, "Error interno al descifrar la clave de recuperación."

    # Re-cifrar con nueva contraseña
    nueva_sal          = os.urandom(16)
    nueva_clave_fernet = derivar_clave_fernet(nueva_contrasena, nueva_sal)
    nuevo_hash_contra  = hashear_contrasena(nueva_contrasena, nueva_sal)
    nueva_cpr_enc      = Fernet(nueva_clave_fernet).encrypt(bytes_cpr)

    with obtener_conexion() as conexion:
        conexion.execute(
            """UPDATE usuarios
               SET hash_contrasena=?, sal=?, clave_privada_enc=?
               WHERE correo=?""",
            (nuevo_hash_contra, nueva_sal, nueva_cpr_enc, correo.strip().lower()),
        )
        conexion.commit()

    return True, "Contraseña restablecida con éxito."


def obtener_perfil_usuario(usuario: str) -> Optional[sqlite3.Row]:
    """Devuelve la fila completa del usuario para la página de perfil."""
    with obtener_conexion() as conexion:
        return conexion.execute(
            "SELECT * FROM usuarios WHERE usuario=?", (usuario,)
        ).fetchone()


def actualizar_perfil_usuario(
    usuario: str,
    nombre_completo: str,
    correo: str,
    fecha_nacimiento: str,
    biografia: str,
) -> tuple[bool, str]:
    """Actualiza datos personales del usuario (sin afectar a la criptografía)."""
    nombre_completo = nombre_completo.strip()
    correo          = correo.strip().lower()
    biografia       = biografia.strip()

    if not nombre_completo:
        return False, "El nombre completo no puede estar vacío."
    if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", correo):
        return False, "Formato de correo no válido."

    with obtener_conexion() as conexion:
        # Verificar que el nuevo correo no pertenece a otro usuario
        conflicto = conexion.execute(
            "SELECT 1 FROM usuarios WHERE correo=? AND usuario!=?",
            (correo, usuario),
        ).fetchone()
        if conflicto:
            return False, "Ese correo ya está siendo usado por otra cuenta."

        conexion.execute(
            """UPDATE usuarios
               SET nombre_completo=?, correo=?, fecha_nacimiento=?, biografia=?
               WHERE usuario=?""",
            (nombre_completo, correo, fecha_nacimiento, biografia, usuario),
        )
        conexion.commit()
    return True, "Perfil actualizado correctamente."


def actualizar_foto_perfil(usuario: str, foto_b64: str) -> tuple[bool, str]:
    """Guarda la foto de perfil (base64) en la BD."""
    with obtener_conexion() as conexion:
        conexion.execute(
            "UPDATE usuarios SET foto_perfil=? WHERE usuario=?",
            (foto_b64, usuario),
        )
        conexion.commit()
    return True, "Foto de perfil actualizada."
