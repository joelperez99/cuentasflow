"""Sidebar de navegación inspirada en Notion."""

import streamlit as st
from streamlit_option_menu import option_menu

from services.auth import AuthService
from utils.constants import APP_NAME, COLOR_PRIMARY, COLOR_TEXT, COLOR_TEXT_SECONDARY


def render_sidebar() -> str:
    """Renderiza la sidebar y devuelve la clave de la página seleccionada."""
    user = AuthService.current_user()

    with st.sidebar:
        st.markdown(
            f"""
            <div style="display:flex;align-items:center;gap:0.6rem;padding:0.4rem 0.2rem 1.2rem 0.2rem;">
                <div style="width:34px;height:34px;border-radius:9px;background:{COLOR_PRIMARY};
                            display:flex;align-items:center;justify-content:center;font-size:18px;">🗂️</div>
                <div style="font-weight:800;font-size:1.15rem;color:{COLOR_TEXT};">{APP_NAME}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        selected = option_menu(
            menu_title=None,
            options=["Dashboard", "Hoy", "Historial", "Configuración"],
            icons=["speedometer2", "pencil-square", "calendar3", "gear"],
            default_index=0,
            styles={
                "container": {"padding": "0", "background-color": "transparent"},
                "icon": {"color": COLOR_TEXT_SECONDARY, "font-size": "16px"},
                "nav-link": {
                    "font-size": "0.92rem",
                    "font-weight": "500",
                    "text-align": "left",
                    "margin": "2px 0",
                    "padding": "0.55rem 0.8rem",
                    "border-radius": "10px",
                    "color": COLOR_TEXT,
                },
                "nav-link-selected": {
                    "background-color": "#ECFDF5",
                    "color": COLOR_PRIMARY,
                    "font-weight": "600",
                },
            },
        )

        st.markdown("<div style='margin-top:auto;'></div>", unsafe_allow_html=True)
        st.divider()

        if user:
            st.markdown(
                f"""
                <div style="display:flex;align-items:center;gap:0.6rem;padding:0.3rem 0.2rem;">
                    <div style="width:32px;height:32px;border-radius:50%;background:{COLOR_PRIMARY};
                                color:white;display:flex;align-items:center;justify-content:center;
                                font-weight:700;font-size:0.85rem;">
                        {user.get("nombre", "?")[:1].upper()}
                    </div>
                    <div style="line-height:1.2;">
                        <div style="font-weight:600;font-size:0.88rem;">{user.get("nombre", "")}</div>
                        <div style="font-size:0.75rem;color:{COLOR_TEXT_SECONDARY};">{user.get("rol", "")}</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button("🚪 Cerrar sesión", use_container_width=True):
                AuthService.logout()
                st.rerun()

    return selected
