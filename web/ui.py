"""
Plantillas y componentes visuales reutilizables.
"""
import streamlit as st
import re

def renderizar_tarjeta_unificada() -> None:
    """
    Tarjeta unificada: logo + título + badges + tabla de variantes ML-DSA
    + enlace a la especificación (todo en la misma tarjeta azul).
    """
    st.markdown("""
    <div style="background:linear-gradient(160deg,#0f1f3d 0%,#0a1628 60%,#071120 100%);
                border:1px solid rgba(94,234,212,0.18);border-radius:20px;
                padding:2.5rem 2rem 2rem;text-align:center;color:white;
                margin-bottom:1.5rem;
                box-shadow:0 0 40px rgba(94,234,212,0.07),0 8px 32px rgba(0,0,0,0.5);">
      <div style="font-size:3rem;line-height:1.2;">🛡️</div>
      <div style="font-size:2.4rem;font-weight:700;margin:0.5rem 0 0.2rem;letter-spacing:0.5px;">Q-Proof Portal</div>
      <div style="opacity:0.65;font-size:0.95rem;margin:0 0 1rem;">Firma digital post-cuántica · Resistente a computación cuántica</div>
      <span style="display:inline-block;background:rgba(94,234,212,0.08);border:1px solid rgba(94,234,212,0.35);color:#5eead4;border-radius:999px;padding:3px 14px;font-size:0.78rem;margin:3px;">FIPS 204</span>
      <span style="display:inline-block;background:rgba(94,234,212,0.08);border:1px solid rgba(94,234,212,0.35);color:#5eead4;border-radius:999px;padding:3px 14px;font-size:0.78rem;margin:3px;">HashML-DSA</span>
      <span style="display:inline-block;background:rgba(94,234,212,0.08);border:1px solid rgba(94,234,212,0.35);color:#5eead4;border-radius:999px;padding:3px 14px;font-size:0.78rem;margin:3px;">SHA-256</span>
      <div style="border-top:1px solid rgba(255,255,255,0.07);margin:1.4rem 0 1.1rem;"></div>
      <div style="font-size:0.83rem;color:#94a3b8;margin-bottom:0.9rem;line-height:1.6;">
        <span style="color:#5eead4;font-weight:600;">ML-DSA</span>
        (Module-Lattice-Based Digital Signature Algorithm) es el estándar
        post-cuántico publicado por el NIST en 2024 como
        <span style="color:#e2e8f0;font-weight:600;">FIPS 204</span>,
        basado en el esquema de retículos CRYSTALS-Dilithium.
      </div>
      <div style="display:grid;grid-template-columns:repeat(4,1fr);font-size:0.82rem;text-align:center;">
        <div style="color:#5eead4;font-weight:600;padding:5px 4px;border-bottom:1px solid rgba(94,234,212,0.2);">Variante</div>
        <div style="color:#5eead4;font-weight:600;padding:5px 4px;border-bottom:1px solid rgba(94,234,212,0.2);">Clave pública</div>
        <div style="color:#5eead4;font-weight:600;padding:5px 4px;border-bottom:1px solid rgba(94,234,212,0.2);">Clave privada</div>
        <div style="color:#5eead4;font-weight:600;padding:5px 4px;border-bottom:1px solid rgba(94,234,212,0.2);">Firma</div>
        <div style="color:#94a3b8;padding:5px 4px;">ML-DSA-44</div><div style="color:#94a3b8;padding:5px 4px;">1 312 B</div><div style="color:#94a3b8;padding:5px 4px;">2 528 B</div><div style="color:#94a3b8;padding:5px 4px;">2 420 B</div>
        <div style="color:#94a3b8;padding:5px 4px;">ML-DSA-65</div><div style="color:#94a3b8;padding:5px 4px;">1 952 B</div><div style="color:#94a3b8;padding:5px 4px;">4 000 B</div><div style="color:#94a3b8;padding:5px 4px;">3 309 B</div>
        <div style="color:#94a3b8;padding:5px 4px;">ML-DSA-87</div><div style="color:#94a3b8;padding:5px 4px;">2 592 B</div><div style="color:#94a3b8;padding:5px 4px;">4 864 B</div><div style="color:#94a3b8;padding:5px 4px;">4 627 B</div>
      </div>
      <a href="https://crystals-dilithium.lovable.app/" target="_blank"
         style="display:inline-block;margin-top:1rem;font-size:0.82rem;color:#5eead4;
                text-decoration:none;border-bottom:1px solid rgba(94,234,212,0.3);padding-bottom:1px;">
        📖 Ver especificación completa → crystals-dilithium.lovable.app
      </a>
    </div>
    """, unsafe_allow_html=True)

def html_fuerza_contrasena(contra: str) -> str:
    """Devuelve HTML con indicadores de requisitos de contraseña."""
    verificaciones = [
        (len(contra) >= 8,               "≥ 8 caracteres"),
        (bool(re.search(r"[A-Z]", contra)), "1 mayúscula"),
        (bool(re.search(r"\d", contra)),    "1 número"),
    ]
    elementos = " &nbsp;·&nbsp; ".join(
        f'<span class="{"ok" if ok else "nok"}">{"✓" if ok else "✗"} {etiqueta}</span>'
        for ok, etiqueta in verificaciones
    )
    return f'<div class="pw-req">{elementos}</div>'

def inicializar_estado_sesion() -> None:
    valores_por_defecto = {
        "sesion_iniciada":  False,
        "usuario":          "",
        "clave_fernet":     None,
        "menu_activo":      "Dashboard",
        # flujo OTP de recuperación
        "codigo_otp":       None,   # str | None
        "correo_otp":       None,   # str | None
        "expiracion_otp":   None,   # datetime | None
        "otp_verificado":   False,
    }
    for clave, valor in valores_por_defecto.items():
        if clave not in st.session_state:
            st.session_state[clave] = valor

def cerrar_sesion() -> None:
    for clave in ("sesion_iniciada", "usuario", "clave_fernet"):
        st.session_state[clave] = False if clave == "sesion_iniciada" else ("" if clave == "usuario" else None)
    st.session_state["menu_activo"] = "Dashboard"

def _ir_al_dashboard() -> None:
    """Callback on_click — escribe ANTES del render siguiente."""
    st.session_state["menu_activo"] = "Dashboard"

def boton_volver(pagina: str = "por_defecto") -> None:
    """Botón retorno: on_click + st.rerun() para máxima fiabilidad."""
    clickeado = st.button(
        "← Volver al Dashboard",
        key=f"btn_volver_{pagina}",
        on_click=_ir_al_dashboard,
    )
    if clickeado:
        st.session_state["menu_activo"] = "Dashboard"
        st.rerun()
    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
