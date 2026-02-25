"""
Lógica para la conexión y manipulación de la Base de Datos SQLite.
"""
import os
try:
    import sqlcipher3 as sqlite3
except ImportError:
    import sqlite3

from dotenv import load_dotenv

load_dotenv()
DB_PASSWORD = os.getenv("DB_PASSWORD")

# DB ubicada en el directorio 'src', un nivel por encima de 'web'
_DIR_WEB = os.path.dirname(os.path.abspath(__file__))
_DIR_SRC = os.path.dirname(_DIR_WEB)
RUTA_BD = os.path.join(_DIR_SRC, "qproof_es.db")

# Esquema extendido: correo, nombre_completo, fecha_nacimiento, cpr_correo_enc (clave de
# recuperación derivada del e-mail), sal_correo (sal para esa derivación)
_ESQUEMA_BD = """
CREATE TABLE IF NOT EXISTS usuarios (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario          TEXT UNIQUE NOT NULL,
    correo           TEXT UNIQUE NOT NULL,
    nombre_completo  TEXT NOT NULL,
    fecha_nacimiento TEXT NOT NULL,
    creado_en        TEXT NOT NULL DEFAULT (datetime('now')),
    foto_perfil      TEXT DEFAULT NULL,
    biografia        TEXT DEFAULT NULL
);

CREATE TABLE IF NOT EXISTS credenciales (
    usuario_id        INTEGER PRIMARY KEY,
    nivel_seguridad   TEXT NOT NULL DEFAULT 'ML_DSA_65',
    hash_contrasena   TEXT NOT NULL,
    sal               BLOB NOT NULL,
    sal_correo        BLOB NOT NULL,
    clave_publica_b64 TEXT NOT NULL,
    clave_privada_enc BLOB NOT NULL,
    cpr_correo_enc    BLOB NOT NULL,
    FOREIGN KEY(usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS seguridad_acceso (
    usuario_id         INTEGER PRIMARY KEY,
    intentos_fallidos  INTEGER NOT NULL DEFAULT 0,
    bloqueado_hasta    TEXT DEFAULT NULL,
    ultimo_otp_enviado TEXT DEFAULT NULL,
    FOREIGN KEY(usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS auditoria_logs (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id  INTEGER NOT NULL,
    accion      TEXT NOT NULL,
    detalles    TEXT DEFAULT NULL,
    fecha_hora  TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY(usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
);
"""

def obtener_conexion() -> sqlite3.Connection:
    conexion = sqlite3.connect(RUTA_BD)
    if DB_PASSWORD:
        conexion.execute(f"PRAGMA key = '{DB_PASSWORD}';")
    conexion.row_factory = sqlite3.Row
    # Habilitar claves foráneas
    conexion.execute("PRAGMA foreign_keys = ON;")
    return conexion

def inicializar_bd() -> None:
    """Crea las tablas si no existen."""
    with obtener_conexion() as conexion:
        conexion.executescript(_ESQUEMA_BD)
        conexion.commit()


