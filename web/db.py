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
    hash_contrasena  TEXT NOT NULL,
    sal              BLOB NOT NULL,
    sal_correo       BLOB NOT NULL,
    clave_publica_b64 TEXT NOT NULL,
    clave_privada_enc BLOB NOT NULL,
    cpr_correo_enc   BLOB NOT NULL,
    creado_en        TEXT NOT NULL DEFAULT (datetime('now')),
    foto_perfil      TEXT DEFAULT NULL,
    biografia        TEXT DEFAULT NULL
);
"""

def obtener_conexion() -> sqlite3.Connection:
    conexion = sqlite3.connect(RUTA_BD)
    if DB_PASSWORD:
        conexion.execute(f"PRAGMA key = '{DB_PASSWORD}';")
    conexion.row_factory = sqlite3.Row
    return conexion

def inicializar_bd() -> None:
    """Crea las tablas si no existen."""
    with obtener_conexion() as conexion:
        conexion.executescript(_ESQUEMA_BD)
        conexion.commit()

def migrar_bd() -> None:
    """
    Añade columnas nuevas a bases de datos ya existentes.
    Ignora silenciosamente el error si la columna ya existe.
    """
    nuevas_columnas = [
        "ALTER TABLE usuarios ADD COLUMN foto_perfil TEXT DEFAULT NULL",
        "ALTER TABLE usuarios ADD COLUMN biografia TEXT DEFAULT NULL",
    ]
    with obtener_conexion() as conexion:
        for sql in nuevas_columnas:
            try:
                conexion.execute(sql)
            except Exception:
                pass   # columna ya existe → OK
        conexion.commit()
