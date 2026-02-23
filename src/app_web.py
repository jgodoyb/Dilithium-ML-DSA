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
