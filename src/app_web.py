"""
Q-Proof System — Web Interface v2 (app_web_v2.py)
==================================================
Versión mejorada del portal web modularizado.
Todo el código está ahora subdividido en la carpeta `src/web/`.

Uso:
    cd src
    streamlit run app_web_v2.py
"""

import os
import sys

# ---------------------------------------------------------------------------
# sys.path — garantiza que el módulo local (src) sea importable
# ---------------------------------------------------------------------------
_SRC_DIR = os.path.dirname(os.path.abspath(__file__))
if _SRC_DIR not in sys.path:
    sys.path.insert(0, _SRC_DIR)

# Importamos y ejecutamos la función principal desde nuestro paquete `web`
from web.main import principal

if __name__ == "__main__":
    principal()
