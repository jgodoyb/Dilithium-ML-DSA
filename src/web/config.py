"""
Configuración global de la aplicación web y utilidades CSS.
"""
import os
import streamlit as st

# ===========================================================================
# CONFIGURACIÓN DE CORREO (via env vars; edita aquí si prefieres hardcodearlo)
# ===========================================================================
SMTP_HOST = os.environ.get("QPROOF_SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("QPROOF_SMTP_PORT", "587"))
SMTP_USER = os.environ.get("QPROOF_SMTP_USER", "jgodoyb19@gmail.com")   # ← pon tu email aquí
SMTP_PASS = os.environ.get("QPROOF_SMTP_PASS", "uhydihdhjzxdezmz")   # ← pon tu App Password aquí

def configurar_pagina():
    st.set_page_config(
        page_title="Q-Proof Portal",
        page_icon="🛡️",
        layout="centered",
        initial_sidebar_state="expanded",
        menu_items={
            "About": (
                "Q-Proof System v2 — Firma post-cuántica ML-DSA (FIPS 204)\n"
                "Especificaciones: https://crystals-dilithium.lovable.app/"
            ),
        },
    )

    st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"], * {
        font-family: 'Inter', 'Segoe UI', sans-serif;
    }

    /* ── Fondo principal negro profundo ──────────────────────────────────── */
    .stApp { background-color: #020617; }
    .block-container { background-color: #020617; padding-top: 2rem !important; }

    /* ── Barra superior: transparente pero con el toggle de sidebar visible ─── */
    header[data-testid="stHeader"] {
        background: transparent !important;
        border-bottom: none !important;
    }
    /* Ocultar solo los botones de Deploy y menú, no el toggle */
    [data-testid="stToolbar"]   { display: none !important; }
    [data-testid="stDecoration"] { display: none !important; }
    #MainMenu { visibility: hidden !important; }
    footer    { visibility: hidden !important; }

    /* File uploader: compact padding, keep text visible */
    [data-testid="stFileUploaderDropzone"] {
        padding: 0.5rem 0.6rem !important;
        min-height: unset !important;
        justify-content: center !important;
    }
    [data-testid="stFileUploaderDropzone"] button {
        font-size: 0.75rem !important;
        padding: 0.25rem 0.8rem !important;
    }

    /* ── Dashboard cards alineadas (mismo min-height en descripción) ─────── */
    .dash-card {
        background: rgba(9,20,42,0.7);
        border: 1px solid rgba(94,234,212,0.1);
        border-radius: 14px;
        padding: 1.4rem 1.2rem 1rem;
        text-align: center;
        height: 100%;
    }
    .dash-card-icon { font-size: 1.8rem; margin-bottom: 0.4rem; }
    .dash-card-title {
        font-size: 1rem; font-weight: 700; color: #f1f5f9;
        margin-bottom: 0.5rem;
    }
    .dash-card-desc {
        font-size: 0.84rem; color: #94a3b8; line-height: 1.45;
        min-height: 52px; margin-bottom: 0.8rem;
    }


    /* ── Inputs ────────────────────────────────────────────────────────── */
    .stTextInput input, input[type="text"], input[type="password"], input[type="email"] {
        background-color: #0d1f3c !important;
        border: 1px solid rgba(94,234,212,0.18) !important;
        border-radius: 8px !important;
        color: #e2e8f0 !important;
        transition: border-color 0.2s, box-shadow 0.2s;
    }
    .stTextInput input:focus, input[type="text"]:focus, input[type="password"]:focus {
        border-color: #5eead4 !important;
        box-shadow: 0 0 0 2px rgba(94,234,212,0.12) !important;
    }
    .stTextInput label, .stDateInput label, .stFileUploader label {
        color: #94a3b8 !important; font-size: 0.85rem !important;
    }

    /* ── Botones primarios → gradiente teal ──────────────────────────────── */
    [data-testid="baseButton-primary"], button[kind="primary"] {
        background: linear-gradient(135deg,#0d9488 0%,#0891b2 100%) !important;
        border: none !important; color: white !important;
        border-radius: 8px !important; font-weight: 600 !important;
        transition: transform 0.15s, box-shadow 0.15s;
    }
    [data-testid="baseButton-primary"]:hover, button[kind="primary"]:hover {
        background: linear-gradient(135deg,#14b8a6 0%,#0ea5e9 100%) !important;
        transform: translateY(-1px);
        box-shadow: 0 4px 14px rgba(94,234,212,0.28) !important;
    }
    [data-testid="baseButton-secondary"], button[kind="secondary"] {
        background: rgba(94,234,212,0.06) !important;
        border: 1px solid rgba(94,234,212,0.25) !important;
        color: #5eead4 !important; border-radius: 8px !important;
    }

    /* ── Tabs ────────────────────────────────────────────────────────────────── */
    .stTabs [data-baseweb="tab-list"] {
        background: transparent !important;
        border-bottom: 1px solid rgba(94,234,212,0.12) !important; gap: 0;
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent !important; color: #475569 !important;
        border-bottom: 2px solid transparent !important;
        padding: 0.5rem 1.1rem !important; font-size: 0.88rem !important;
    }
    .stTabs [aria-selected="true"] {
        color: #5eead4 !important; border-bottom-color: #5eead4 !important;
        background: transparent !important;
    }

    /* ── Formularios y Expanders ─────────────────────────────────────────── */
    [data-testid="stForm"] {
        border: 1px solid rgba(94,234,212,0.1) !important;
        border-radius: 12px !important; padding: 1.2rem 1.4rem !important;
        background: rgba(9,20,42,0.7) !important;
    }
    [data-testid="stExpander"] {
        border: 1px solid rgba(94,234,212,0.1) !important;
        border-radius: 10px !important; background: rgba(9,20,42,0.5) !important;
    }
    [data-testid="stExpander"] summary { color: #94a3b8 !important; }

    /* ── Alertas ───────────────────────────────────────────────────────────── */
    [data-testid="stInfo"]    { background:rgba(14,165,233,0.08)!important; border-left-color:#38bdf8!important; border-radius:8px!important; color:#7dd3fc!important; }
    [data-testid="stSuccess"] { background:rgba(94,234,212,0.08)!important; border-left-color:#5eead4!important; border-radius:8px!important; color:#5eead4!important; }
    [data-testid="stError"]   { background:rgba(248,113,113,0.08)!important; border-left-color:#f87171!important; border-radius:8px!important; }
    [data-testid="stWarning"] { background:rgba(251,191,36,0.07)!important; border-left-color:#fbbf24!important; border-radius:8px!important; color:#fbbf24!important; }

    /* ── Métricas ──────────────────────────────────────────────────────────── */
    [data-testid="stMetricValue"] { color:#5eead4!important; font-size:1rem!important; }
    [data-testid="stMetricLabel"] { color:#64748b!important; font-size:0.75rem!important; }

    /* ── Tablas markdown ───────────────────────────────────────────────────── */
    table { border-collapse: collapse !important; width: 100% !important; }
    th { color:#5eead4!important; border-bottom:1px solid rgba(94,234,212,0.2)!important; padding:6px 12px!important; font-size:0.82rem!important; background:rgba(94,234,212,0.04)!important; }
    td { color:#94a3b8!important; border-bottom:1px solid rgba(30,58,110,0.3)!important; padding:5px 12px!important; font-size:0.82rem!important; }

    /* ── Texto general ───────────────────────────────────────────────────── */
    h1, h2, h3, h4 { color: #f1f5f9 !important; }
    p, li { color: #cbd5e1; }
    a { color: #5eead4 !important; }
    code { background:rgba(94,234,212,0.08)!important; color:#5eead4!important; border-radius:4px; }

    /* ── File uploader ───────────────────────────────────────────────────── */
    [data-testid="stFileUploader"] {
        background: rgba(9,20,42,0.6) !important;
        border: 1px dashed rgba(94,234,212,0.2) !important;
        border-radius: 10px !important;
    }

    /* ── Separadores ────────────────────────────────────────────────────── */
    hr, hr.light { border-color: rgba(94,234,212,0.1) !important; margin: 1.2rem 0 !important; }

    /* ── Indicador de fuerza de contraseña ───────────────────────────────── */
    .pw-req {
        font-size: 0.77rem; color: #94a3b8;
        background: rgba(9,20,42,0.8); border: 1px solid rgba(94,234,212,0.15);
        border-radius: 8px; padding: 0.45rem 0.8rem; margin-top: 0.3rem;
    }
    .pw-req .ok  { color: #5eead4; }
    .pw-req .nok { color: #f87171; }

    /* ── Scrollbar ──────────────────────────────────────────────────────────── */
    ::-webkit-scrollbar       { width: 6px; }
    ::-webkit-scrollbar-track { background: #020617; }
    ::-webkit-scrollbar-thumb { background: rgba(94,234,212,0.25); border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: rgba(94,234,212,0.45); }
</style>
    """, unsafe_allow_html=True)
