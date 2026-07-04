"""Inyección de CSS personalizado para que Streamlit se sienta como un SaaS premium."""

import streamlit as st

from utils.constants import (
    COLOR_BG,
    COLOR_BORDER,
    COLOR_CARD,
    COLOR_DANGER,
    COLOR_DANGER_HOVER,
    COLOR_PRIMARY,
    COLOR_PRIMARY_HOVER,
    COLOR_TEXT,
    COLOR_TEXT_SECONDARY,
)


def inject_global_styles() -> None:
    """Inyecta el CSS global que oculta el chrome de Streamlit y aplica el look SaaS."""
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

        html, body, [class*="css"] {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        }}

        /* Oculta el chrome nativo de Streamlit, pero conserva el boton para
           abrir/cerrar la sidebar (vive dentro de stToolbar/header). */
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        header {{background: transparent !important; box-shadow: none !important;}}
        [data-testid="stDecoration"] {{display: none;}}
        [data-testid="stStatusWidget"] {{display: none;}}
        [data-testid="stAppDeployButton"] {{display: none;}}
        [data-testid="stMainMenu"] {{display: none;}}

        .stApp {{
            background-color: {COLOR_BG};
        }}

        [data-testid="stAppViewContainer"] > .main {{
            background-color: {COLOR_BG};
        }}

        .block-container {{
            padding-top: 2rem;
            padding-bottom: 3rem;
            padding-left: 2.5rem;
            padding-right: 2.5rem;
            max-width: 100%;
        }}

        h1, h2, h3, h4 {{
            color: {COLOR_TEXT};
            font-weight: 800 !important;
            letter-spacing: -0.02em;
        }}

        p, span, label, div {{
            color: {COLOR_TEXT};
        }}

        .app-subtitle {{
            color: {COLOR_TEXT_SECONDARY};
            font-size: 0.95rem;
            margin-top: -0.6rem;
            margin-bottom: 1.5rem;
        }}

        /* --- Sidebar estilo Notion --- */
        [data-testid="stSidebar"] {{
            background-color: #FFFFFF;
            border-right: 1px solid {COLOR_BORDER};
        }}
        [data-testid="stSidebar"] > div:first-child {{
            padding-top: 1.2rem;
        }}

        /* --- Inputs modernos --- */
        input, textarea, .stTextInput input, .stTextArea textarea, .stDateInput input {{
            border-radius: 10px !important;
            border: 1px solid {COLOR_BORDER} !important;
            background-color: #FFFFFF !important;
            padding: 0.55rem 0.8rem !important;
            transition: border-color 0.15s ease, box-shadow 0.15s ease;
        }}
        input:focus, textarea:focus, .stTextInput input:focus {{
            border-color: {COLOR_PRIMARY} !important;
            box-shadow: 0 0 0 3px rgba(34, 197, 94, 0.15) !important;
            outline: none !important;
        }}

        /* --- Botones --- */
        .stButton > button {{
            border-radius: 10px;
            font-weight: 600;
            padding: 0.5rem 1.2rem;
            border: 1px solid {COLOR_BORDER};
            background-color: #FFFFFF;
            color: {COLOR_TEXT};
            transition: all 0.15s ease;
        }}
        .stButton > button:hover {{
            border-color: {COLOR_PRIMARY};
            color: {COLOR_PRIMARY_HOVER};
            transform: translateY(-1px);
        }}

        .stButton > button[kind="primary"] {{
            background-color: {COLOR_PRIMARY};
            border: none;
            color: white;
            box-shadow: 0 1px 2px rgba(0,0,0,0.08);
        }}
        .stButton > button[kind="primary"]:hover {{
            background-color: {COLOR_PRIMARY_HOVER};
            color: white;
            transform: translateY(-1px);
            box-shadow: 0 4px 10px rgba(34, 197, 94, 0.35);
        }}

        /* --- Tarjetas genéricas --- */
        .app-card {{
            background-color: {COLOR_CARD};
            border: 1px solid {COLOR_BORDER};
            border-radius: 16px;
            padding: 1.2rem 1.4rem;
            box-shadow: 0 1px 2px rgba(0,0,0,0.03);
            transition: box-shadow 0.2s ease, transform 0.2s ease;
        }}
        .app-card:hover {{
            box-shadow: 0 8px 20px rgba(0,0,0,0.06);
        }}

        .info-banner {{
            background: linear-gradient(135deg, #ECFDF5 0%, #F0FDF4 100%);
            border: 1px solid #BBF7D0;
            border-radius: 16px;
            padding: 1.1rem 1.4rem;
            display: flex;
            align-items: center;
            gap: 0.8rem;
            margin-bottom: 1.4rem;
            animation: fadeIn 0.4s ease;
        }}

        .metric-tile {{
            background-color: {COLOR_CARD};
            border: 1px solid {COLOR_BORDER};
            border-radius: 14px;
            padding: 1rem 1.2rem;
            text-align: left;
        }}
        .metric-tile .metric-label {{
            font-size: 0.78rem;
            color: {COLOR_TEXT_SECONDARY};
            text-transform: uppercase;
            letter-spacing: 0.04em;
            font-weight: 600;
        }}
        .metric-tile .metric-value {{
            font-size: 1.6rem;
            font-weight: 800;
            color: {COLOR_TEXT};
            margin-top: 0.2rem;
        }}

        .pill {{
            display: inline-block;
            padding: 0.15rem 0.65rem;
            border-radius: 999px;
            font-size: 0.75rem;
            font-weight: 600;
            background-color: #ECFDF5;
            color: {COLOR_PRIMARY_HOVER};
            border: 1px solid #BBF7D0;
        }}

        /* --- Animaciones --- */
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(4px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        @keyframes scaleIn {{
            from {{ opacity: 0; transform: scale(0.96); }}
            to {{ opacity: 1; transform: scale(1); }}
        }}
        .fade-in {{ animation: fadeIn 0.35s ease; }}
        .scale-in {{ animation: scaleIn 0.25s ease; }}

        /* --- Dialog / Modal (st.dialog) --- */
        [data-testid="stDialog"] > div {{
            border-radius: 20px !important;
            animation: scaleIn 0.2s ease;
            box-shadow: 0 20px 60px rgba(0,0,0,0.25) !important;
        }}

        /* --- Divider sutil --- */
        hr {{
            border-color: {COLOR_BORDER};
        }}

        .danger-text {{ color: {COLOR_DANGER}; }}
        .danger-text:hover {{ color: {COLOR_DANGER_HOVER}; }}

        /* Option menu overrides para look Notion */
        .nav-link {{
            border-radius: 10px !important;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )
