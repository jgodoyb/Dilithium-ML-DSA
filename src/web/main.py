import streamlit as st

from .config import configurar_pagina
from .db import inicializar_bd, migrar_bd
from .ui import inicializar_estado_sesion
from .views import (
    pagina_login, pagina_dashboard, pagina_perfil,
    pagina_firmar, pagina_verificar
)

def principal() -> None:
    # 1. Configurar la página (debe ser la primera llamada de Streamlit)
    configurar_pagina()

    # 2. Inicializar base de datos y estado de sesión
    inicializar_bd()
    migrar_bd()
    inicializar_estado_sesion()

    # 3. Enrutamiento del contenido principal
    if not st.session_state.sesion_iniciada:
        pagina_login()
        return

    menu = st.session_state.menu_activo
    if   menu == "Dashboard":           pagina_dashboard()
    elif menu == "Mi Perfil":           pagina_perfil()
    elif menu == "Firmar Documento":    pagina_firmar()
    elif menu == "Verificar Documento": pagina_verificar()
