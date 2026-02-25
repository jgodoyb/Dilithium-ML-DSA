"""
Vistas de las diferentes páginas de la aplicación Streamlit.
"""
import streamlit as st
import datetime
import random
import base64
import os
import sys

from .ui import renderizar_tarjeta_unificada, html_fuerza_contrasena, cerrar_sesion, boton_volver
from .auth import (
    iniciar_sesion, registrar_usuario, restablecer_contrasena_con_correo, obtener_usuario_por_correo,
    obtener_perfil_usuario, actualizar_perfil_usuario, actualizar_foto_perfil,
    obtener_clave_privada, obtener_clave_publica, registrar_auditoria_por_usuario
)
from .email_sender import enviar_correo_otp
from .signature import construir_archivo_firma, analizar_archivo_firma, _ALGORITMO_PH, _CONTEXTO

# Importar MLDSA
_DIR_WEB = os.path.dirname(os.path.abspath(__file__))
_DIR_SRC = os.path.dirname(_DIR_WEB)
if _DIR_SRC not in sys.path:
    sys.path.insert(0, _DIR_SRC)
import mldsa

# ---------------------------------------------------------------------------
# LOGIN / REGISTRO / RECUPERACIÓN
# ---------------------------------------------------------------------------
def pagina_login() -> None:
    renderizar_tarjeta_unificada()
    st.markdown("<hr class='light'>", unsafe_allow_html=True)

    pestana_login, pestana_reg, pestana_recuperar = st.tabs([
        "🔑 Iniciar Sesión",
        "📝 Crear Cuenta",
        "🔓 Recuperar Contraseña",
    ])

    # ── TAB: Iniciar Sesión ──────────────────────────────────────────────
    with pestana_login:
        with st.form("formulario_login", clear_on_submit=False):
            input_usuario = st.text_input("Usuario", placeholder="Tu nombre de usuario")
            input_contra  = st.text_input("Contraseña", type="password", placeholder="••••••••")
            enviado = st.form_submit_button("Entrar →", type="primary", use_container_width=True)

        if enviado:
            if not input_usuario or not input_contra:
                st.warning("⚠️ Por favor completa todos los campos.")
            else:
                with st.spinner("Autenticando…"):
                    exito, clave_fernet, mensaje_error = iniciar_sesion(input_usuario, input_contra)
                if exito:
                    st.session_state.sesion_iniciada = True
                    st.session_state.usuario         = input_usuario.strip()
                    st.session_state.clave_fernet    = clave_fernet
                    st.rerun()
                else:
                    st.error(f"❌ {mensaje_error}")

    # ── TAB: Crear Cuenta ────────────────────────────────────────────────
    with pestana_reg:
        st.info(
            "Tu clave privada ML-DSA se cifrará con tu contraseña "
            "(AES-256, nunca en texto plano). "
        )

        with st.form("formulario_registro", clear_on_submit=True):
            col_a, col_b = st.columns(2)
            with col_a:
                reg_usuario      = st.text_input("Nombre de usuario *",  placeholder="mínimo 3 caracteres")
                reg_correo       = st.text_input("E-mail *",              placeholder="usuario@ejemplo.com")
            with col_b:
                reg_nombre       = st.text_input("Nombre completo *",     placeholder="Nombre y Apellidos")
                reg_nacimiento   = st.date_input(
                    "Fecha de nacimiento *",
                    value=datetime.date(2000, 1, 1),
                    min_value=datetime.date(1900, 1, 1),
                    max_value=datetime.date.today(),
                )

            st.markdown("---")
            reg_contra   = st.text_input("Contraseña *",         type="password", placeholder="••••••••")
            reg_contra2  = st.text_input("Confirmar contraseña *", type="password", placeholder="repite la contraseña")

            st.markdown("---")
            st.markdown("**Nivel de Seguridad Post-Cuántica**")
            reg_nivel = st.selectbox(
                "Algoritmo ML-DSA",
                options=["ML_DSA_44", "ML_DSA_65", "ML_DSA_87"],
                index=1,
                help="Elige el tamaño de la matriz y parámetros. ML-DSA-44 es el más ligero, ML-DSA-87 el más fuerte."
            )

            # Indicador visual de requisitos (solo si el campo tiene texto)
            if reg_contra:
                st.markdown(html_fuerza_contrasena(reg_contra), unsafe_allow_html=True)
            else:
                st.markdown(
                    '<div class="pw-req" style="color:#475569;">'
                    'La contraseña debe tener ≥ 8 caracteres, 1 mayúscula y 1 número.</div>',
                    unsafe_allow_html=True,
                )

            enviado_registro = st.form_submit_button(
                "Crear Cuenta", type="primary", use_container_width=True
            )

        if enviado_registro:
            if reg_contra != reg_contra2:
                st.error("❌ Las contraseñas no coinciden.")
            else:
                with st.spinner(f"Generando par de claves ({reg_nivel})… puede tardar unos segundos."):
                    exito, mensaje = registrar_usuario(
                        reg_usuario, reg_correo, reg_nombre,
                        reg_nacimiento.isoformat(), reg_contra, reg_nivel
                    )
                if exito:
                    st.success(f"✅ {mensaje} Ya puedes iniciar sesión.")
                else:
                    st.error(f"❌ {mensaje}")

    # ── TAB: Recuperar Contraseña ────────────────────────────────────────
    with pestana_recuperar:

        # ── PASO 3 — Éxito ───────────────────────────────────────────────
        if st.session_state.fase_recuperacion == 3:
            st.success("✅ Contraseña restablecida correctamente. Ya puedes iniciar sesión.")
            if st.button("← Volver al inicio de sesión", use_container_width=True):
                st.session_state.fase_recuperacion = 1
                st.session_state.otp_verificado = False
                st.rerun()

        # ── PASO 2 — Introducir OTP + nueva contraseña ───────────────────
        elif st.session_state.fase_recuperacion == 2:
            st.info(
                f"📬 Si el correo **{st.session_state.correo_otp}** está registrado, hemos enviado un código de 6 dígitos. "
                "Introdúcelo aquí junto con tu nueva contraseña.",
                icon="🔢",
            )

            with st.form("formulario_verificar_otp"):
                input_otp = st.text_input(
                    "Código recibido por e-mail",
                    max_chars=6,
                    placeholder="123456",
                )
                nueva_contra  = st.text_input("Nueva contraseña",     type="password", placeholder="••••••••")
                nueva_contra2 = st.text_input("Confirmar contraseña", type="password", placeholder="••••••••")

                if nueva_contra:
                    st.markdown(html_fuerza_contrasena(nueva_contra), unsafe_allow_html=True)

                btn_verificar = st.form_submit_button(
                    "✅ Restablecer contraseña", type="primary", use_container_width=True
                )

            if btn_verificar:
                ahora    = datetime.datetime.utcnow()
                expirado = (
                    not st.session_state.codigo_otp
                    or st.session_state.expiracion_otp is None
                    or ahora > st.session_state.expiracion_otp
                )
                
                # Si no se generó OTP real (correo no existía), siempre fallará aquí silenciosamente
                if expirado or input_otp.strip() != st.session_state.codigo_otp:
                    st.error("❌ Código incorrecto o expirado. Comprueba el e-mail e inténtalo de nuevo.")
                elif nueva_contra != nueva_contra2:
                    st.error("❌ Las contraseñas no coinciden.")
                else:
                    exito, mensaje = restablecer_contrasena_con_correo(st.session_state.correo_otp, nueva_contra)
                    if exito:
                        st.session_state.codigo_otp     = None
                        st.session_state.correo_otp     = None
                        st.session_state.expiracion_otp = None
                        st.session_state.otp_verificado = True
                        st.session_state.fase_recuperacion = 3
                        st.rerun()
                    else:
                        st.error(f"❌ {mensaje}")

            st.markdown("---")
            if st.button("← No recibí el código — volver a solicitarlo", use_container_width=True):
                st.session_state.fase_recuperacion = 1
                st.session_state.codigo_otp     = None
                st.session_state.correo_otp     = None
                st.session_state.expiracion_otp = None
                st.rerun()

        # ── PASO 1 — Pedir e-mail ────────────────────────────────────────
        else:
            st.info(
                "Introduce el e-mail con el que te registraste. "
                "Te enviaremos un código de 6 dígitos válido durante 10 minutos.",
                icon="📧",
            )
            with st.form("formulario_solicitar_otp"):
                correo_recuperar = st.text_input(
                    "E-mail registrado", placeholder="usuario@ejemplo.com"
                )
                btn_enviar = st.form_submit_button(
                    "📨 Enviar código", type="primary", use_container_width=True
                )

            if btn_enviar:
                if not correo_recuperar:
                    st.warning("⚠️ Introduce tu e-mail.")
                else:
                    import time
                    from .auth import registrar_envio_otp
                    
                    ahora = datetime.datetime.utcnow()
                    
                    # 1. Rate limiting por sesión (prevenir clics rápidos)
                    if st.session_state.bloqueo_solicitud_otp and ahora < st.session_state.bloqueo_solicitud_otp:
                        st.error("Espera unos segundos antes de volver a solicitar un código.")
                    else:
                        st.session_state.bloqueo_solicitud_otp = ahora + datetime.timedelta(seconds=30)
                        
                        correo_limpio = correo_recuperar.strip().lower()
                        
                        with st.spinner("Procesando solicitud..."):
                            # Anti-enumeración: siempre hacemos una pausa artificial fija
                            time.sleep(1.5) 
                            
                            fila = obtener_usuario_por_correo(correo_limpio)
                            
                            st.session_state.correo_otp = correo_limpio
                            st.session_state.codigo_otp = None
                            
                            if fila:
                                # 2. Rate limiting por correo en Base de Datos (ej. 2 minutos)
                                enviar_real = True
                                if fila["ultimo_otp_enviado"]:
                                    ultimo_envio = datetime.datetime.fromisoformat(fila["ultimo_otp_enviado"])
                                    if (ahora - ultimo_envio).total_seconds() < 120:  # 2 minutos
                                        enviar_real = False
                                
                                if enviar_real:
                                    otp = f"{random.randint(0, 999999):06d}"
                                    ok_correo, error = enviar_correo_otp(correo_limpio, fila["usuario"], otp)
                                    if ok_correo:
                                        st.session_state.codigo_otp = otp
                                        st.session_state.expiracion_otp = ahora + datetime.timedelta(minutes=10)
                                        registrar_envio_otp(correo_limpio)
                                        
                            # Siempre avanzamos a la fase 2 para no dar pistas
                            st.session_state.fase_recuperacion = 2
                            st.rerun()


# ---------------------------------------------------------------------------
# PERFIL DE USUARIO
# ---------------------------------------------------------------------------
def pagina_perfil() -> None:
    """Página de perfil tipo Instagram: foto, datos, edición."""
    boton_volver()
    fila = obtener_perfil_usuario(st.session_state.usuario)
    if not fila:
        st.error("No se pudo cargar el perfil.")
        return

    bytes_cp = base64.b64decode(fila["clave_publica_b64"])

    # ── CABECERA: avatar + info principal ─────────────────────────────────
    col_foto, col_info = st.columns([1, 2.8], gap="large")

    with col_foto:
        if fila["foto_perfil"]:
            src_img = f"data:image/jpeg;base64,{fila['foto_perfil']}"
        else:
            # Avatar por defecto: gradiente teal con iniciales
            iniciales = "".join(w[0].upper() for w in fila["nombre_completo"].split()[:2])
            src_img = None

        if src_img:
            st.markdown(
                f'<img src="{src_img}" '
                'style="width:110px;height:110px;border-radius:50%;'
                'object-fit:cover;border:3px solid #5eead4;'
                'box-shadow:0 0 20px rgba(94,234,212,0.3);">',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f'<div style="width:110px;height:110px;border-radius:50%;'
                'background:linear-gradient(135deg,#0d9488,#0891b2);'
                'display:flex;align-items:center;justify-content:center;'
                'font-size:2.2rem;font-weight:700;color:white;'
                'border:3px solid #5eead4;'
                'box-shadow:0 0 20px rgba(94,234,212,0.3);">'
                f'{iniciales}</div>',
                unsafe_allow_html=True,
            )

        # Espacio entre avatar y uploader, luego uploader en tamaño natural
        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        nueva_foto = st.file_uploader(
            "Foto", type=["png"],
            label_visibility="collapsed",
            key="subida_foto_perfil",
        )
        if nueva_foto:
            foto_b64 = base64.b64encode(nueva_foto.getvalue()).decode("ascii")
            exito, mensaje = actualizar_foto_perfil(st.session_state.usuario, foto_b64)
            if exito:
                st.success("✔ Actualizada")
                st.rerun()
            else:
                st.error(mensaje)

    with col_info:
        st.markdown(
            f'<div style="margin-top:6px;">'
            f'<div style="font-size:1.7rem;font-weight:700;color:#f1f5f9;'
            f'letter-spacing:0.3px;">{st.session_state.usuario}</div>'
            f'<div style="font-size:1rem;color:#94a3b8;margin:2px 0 6px;">{fila["nombre_completo"]}</div>'
            f'<div style="font-size:0.82rem;color:#5eead4;margin-bottom:4px;">'
            f'{fila["correo"]}</div>'
            f'<div style="font-size:0.8rem;color:#64748b;">'
            f'{fila["fecha_nacimiento"]}  ·  Miembro desde {(fila["creado_en"] or "")[:10]}'
            f'</div>',
            unsafe_allow_html=True,
        )
        if fila["biografia"]:
            st.markdown(
                f'<div style="margin-top:10px;font-size:0.88rem;color:#cbd5e1;'
                f'background:rgba(14,30,60,0.6);border-left:3px solid #5eead4;'
                f'border-radius:0 8px 8px 0;padding:6px 12px;">{fila["biografia"]}</div>',
                unsafe_allow_html=True,
            )

        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        nivel_usuario = fila["nivel_seguridad"] if "nivel_seguridad" in fila.keys() else "ML_DSA_65"
        c1.metric("Algoritmo", nivel_usuario.replace("_", "-"))
        c2.metric("Clave pública", f"{len(bytes_cp)} B")
        c3.metric("Estándar", "FIPS 204")

    st.markdown("---")

    # ── EDITAR DATOS ────────────────────────────────────────────────────────
    with st.expander("Editar datos personales", expanded=False):
        with st.form("formulario_editar_perfil"):
            col_a, col_b = st.columns(2)
            with col_a:
                e_nombre = st.text_input(
                    "Nombre completo", value=fila["nombre_completo"]
                )
                e_correo = st.text_input(
                    "E-mail", value=fila["correo"]
                )
            with col_b:
                try:
                    fn_defecto = datetime.date.fromisoformat(fila["fecha_nacimiento"])
                except Exception:
                    fn_defecto = datetime.date(2000, 1, 1)
                e_nacimiento = st.date_input(
                    "Fecha de nacimiento", value=fn_defecto,
                    min_value=datetime.date(1900, 1, 1),
                    max_value=datetime.date.today(),
                )
            e_bio = st.text_area(
                "Bio (descripción corta)",
                value=fila["biografia"] or "",
                max_chars=160,
                placeholder="Cuéntanos algo sobre ti... (máx. 160 car.)",
                height=70,
            )
            btn_guardar = st.form_submit_button(
                "Guardar cambios", type="primary", use_container_width=True
            )

        if btn_guardar:
            exito, mensaje = actualizar_perfil_usuario(
                st.session_state.usuario,
                e_nombre, e_correo, e_nacimiento.isoformat(), e_bio,
            )
            if exito:
                st.success(f"✅ {mensaje}")
                st.rerun()
            else:
                st.error(f"❌ {mensaje}")

    # ── CLAVE PÚBLICA ──────────────────────────────────────────────────────────
    with st.expander("Clave pública ML-DSA", expanded=False):
        cp_hex = bytes_cp.hex()
        st.markdown(
            '| Campo | Valor |\n|---|---|\n'
            f'| Tamaño | `{len(bytes_cp)} bytes` |\n'
            f'| Algoritmo | `HashML-DSA / SHA-256` |\n'
            f'| Primeros 32 B (hex) | `{cp_hex[:64]}…` |'
        )
        st.download_button(
            "⬇️ Descargar clave pública (hex)",
            data=cp_hex,
            file_name=f"pubkey_{st.session_state.usuario}.hex",
            mime="text/plain",
        )


# ---------------------------------------------------------------------------
# DASHBOARD
# ---------------------------------------------------------------------------
def pagina_dashboard() -> None:
    # Barra superior: nombre de usuario + cerrar sesión
    col_titulo, col_salir = st.columns([4, 1])
    with col_titulo:
        st.title(f"Bienvenido, {st.session_state.usuario}")
    with col_salir:
        st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)
        st.button("Cerrar Sesión", on_click=cerrar_sesion, type="primary",
                  use_container_width=True, key="salir_dashboard")
    st.markdown("---")

    col1, col2, col3 = st.columns(3)
    _TARJETAS = [
        (col1, "📷", "Mi Perfil",
         "Edita tus datos y foto de perfil, consulta tu clave pública ML-DSA.",
         "Ver perfil →", "Mi Perfil"),
        (col2, "🖊️", "Firmar documento",
         "Sube un PDF y obtén un archivo .sig con tu firma post-cuántica ML-DSA.",
         "Ir a Firmar →", "Firmar Documento"),
        (col3, "✅", "Verificar firma",
         "Comprueba la autenticidad de un PDF y que la firma pertenece al firmante.",
         "Ir a Verificar →", "Verificar Documento"),
    ]
    for col, icono, titulo, desc, etiqueta_btn, objetivo in _TARJETAS:
        with col:
            st.markdown(
                f'<div class="dash-card">'
                f'<div class="dash-card-icon">{icono}</div>'
                f'<div class="dash-card-title">{titulo}</div>'
                f'<div class="dash-card-desc">{desc}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
            if st.button(etiqueta_btn, use_container_width=True, key=f"dash_{objetivo}"):
                st.session_state.menu_activo = objetivo
                st.rerun()

    st.markdown("---")

    with st.expander("Especificación ML-DSA / FIPS 204", expanded=False):
        st.markdown(
            "Consulta la especificación completa del algoritmo: "
            "[crystals-dilithium.lovable.app](https://crystals-dilithium.lovable.app/)"
        )


# ---------------------------------------------------------------------------
# FIRMAR DOCUMENTO
# ---------------------------------------------------------------------------
def pagina_firmar() -> None:
    boton_volver("firmar")
    st.header("🖊️ Firmar PDF")
    st.caption("HashML-DSA (SHA-256) con tu clave privada ML-DSA (FIPS 204).")
    st.markdown("---")

    pdf_subido = st.file_uploader("Selecciona el archivo PDF a firmar", type="pdf")
    if pdf_subido is None:
        st.info("⬆️ Sube un PDF para comenzar.")
        return

    col1, col2 = st.columns(2)
    col1.metric("Archivo", pdf_subido.name)
    col2.metric("Tamaño", f"{round(len(pdf_subido.getvalue())/1024, 1)} KB")
    st.markdown("---")

    if st.button("✅ Firmar Documento", type="primary", use_container_width=True):
        with st.spinner("Descifrando clave privada…"):
            bytes_cpr = obtener_clave_privada(st.session_state.usuario, st.session_state.clave_fernet)

        if bytes_cpr is None:
            st.error("❌ No se pudo recuperar la clave privada. Cierra sesión e inténtalo de nuevo.")
            return

        try:
            with st.spinner("Aplicando firma post-cuántica HashML-DSA…"):
                perfil = obtener_perfil_usuario(st.session_state.usuario)
                nivel = perfil["nivel_seguridad"] if perfil and "nivel_seguridad" in perfil.keys() else "ML_DSA_65"
                firma_binaria = mldsa.hash_sign(
                    bytes_cpr, pdf_subido.getvalue(), ph_algo=_ALGORITMO_PH, ctx=_CONTEXTO, level=nivel
                )
        except Exception as exc:
            st.error(f"❌ Error durante la firma: {exc}")
            return

        contenido_firma = construir_archivo_firma(firma_binaria, st.session_state.usuario, pdf_subido.name)
        registrar_auditoria_por_usuario(st.session_state.usuario, "SIGNATURE_GENERATED", f"Documento: {pdf_subido.name}")
        st.success(f"✅ Documento firmado. Tamaño de firma: **{len(firma_binaria)} bytes**.")

        with st.expander("📄 Vista previa del archivo .sig", expanded=True):
            st.code(contenido_firma, language="text")

        st.download_button(
            label="⬇️ Descargar Firma (.sig)",
            data=contenido_firma.encode("utf-8"),
            file_name=f"{pdf_subido.name}.sig",
            mime="text/plain",
            use_container_width=True,
            type="primary",
        )


# ---------------------------------------------------------------------------
# VERIFICAR FIRMA
# ---------------------------------------------------------------------------
def pagina_verificar() -> None:
    boton_volver("verificar")
    st.header("✅ Verificar Firma de PDF")
    st.caption("Comprueba que el PDF no ha sido alterado y que la firma es auténtica.")
    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        pdf_verificar = st.file_uploader("1️⃣ Archivo PDF original", type="pdf", key="verificar_pdf")
    with col2:
        firma_verificar = st.file_uploader("2️⃣ Archivo de firma (.sig)", type=["sig", "txt"], key="verificar_firma")

    nombre_firmante = st.text_input(
        "3️⃣ Nombre de usuario del firmante",
        placeholder="usuario que generó la firma",
    )
    st.markdown("---")

    if st.button("🔍 Verificar Autenticidad", type="primary", use_container_width=True):
        faltantes = [n for cond, n in [
            (pdf_verificar  is None, "PDF original"),
            (firma_verificar  is None, "archivo .sig"),
            (not nombre_firmante,     "nombre del firmante"),
        ] if cond]
        if faltantes:
            st.warning(f"⚠️ Falta: {', '.join(faltantes)}.")
            return

        bytes_cp = obtener_clave_publica(nombre_firmante.strip())
        if bytes_cp is None:
            st.error(f"❌ El usuario **'{nombre_firmante}'** no existe en la base de datos.")
            return

        try:
            texto_firma = firma_verificar.getvalue().decode("utf-8")
        except UnicodeDecodeError:
            st.error("❌ El archivo .sig no es texto UTF-8 válido.")
            return

        firma_binaria = analizar_archivo_firma(texto_firma)
        if firma_binaria is None:
            st.error("❌ El archivo .sig no tiene el formato esperado o ha sido modificado.")
            return

        datos_pdf = pdf_verificar.getvalue()
        
        perfil_firmante = obtener_perfil_usuario(nombre_firmante.strip())
        nivel_firmante = perfil_firmante["nivel_seguridad"] if perfil_firmante and "nivel_seguridad" in perfil_firmante.keys() else "ML_DSA_65"

        try:
            with st.spinner(f"Comprobando retículos criptográficos ({nivel_firmante})…"):
                es_valida = mldsa.hash_verify(
                    bytes_cp, datos_pdf, firma_binaria, ph_algo=_ALGORITMO_PH, ctx=_CONTEXTO, level=nivel_firmante
                )
        except Exception as exc:
            st.error(f"❌ Error técnico en la verificación: {exc}")
            return

        if es_valida:
            registrar_auditoria_por_usuario(st.session_state.usuario, "SIGNATURE_VERIFIED", f"Documento: {pdf_verificar.name}, Firmante: {nombre_firmante.strip()}")
            st.success(
                f"✅ **LA FIRMA ES VÁLIDA.** "
                f"El documento fue firmado por **{nombre_firmante}** y no ha sido alterado."
            )
        else:
            st.error(
                "❌ **LA FIRMA NO ES VÁLIDA.** "
                "El documento fue alterado o la firma no corresponde a este archivo/firmante."
            )

        with st.expander("🔬 Detalles técnicos"):
            st.markdown(f"""
            | Parámetro | Valor |
            |-----------|-------|
            | Algoritmo | `HashML-DSA / {_ALGORITMO_PH}` |
            | Contexto (ctx) | `{_CONTEXTO.decode()}` |
            | Firmante | `{nombre_firmante}` |
            | Tamaño PDF | `{round(len(datos_pdf)/1024, 1)} KB` |
            | Tamaño firma | `{len(firma_binaria)} bytes` |
            | Tamaño clave pública | `{len(bytes_cp)} bytes` |
            | Resultado | `{"VÁLIDA ✅" if es_valida else "INVÁLIDA ❌"}` |
            | Especificación | [crystals-dilithium.lovable.app](https://crystals-dilithium.lovable.app/) |
            """)
