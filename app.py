"""Punto de entrada de la aplicación: login, enrutamiento y layout general."""

import os

import streamlit as st

from components.sidebar import render_sidebar
from database.google_sheet import get_sheets_service
from pages import configuracion, dashboard, historial, hoy
from services.accounts import AccountService
from services.auth import AuthService
from utils.constants import APP_NAME, APP_TAGLINE
from utils.styles import inject_global_styles

st.set_page_config(page_title=APP_NAME, page_icon="🗂️", layout="wide", initial_sidebar_state="expanded")


def render_login(auth_service: AuthService) -> None:
    """Renderiza la pantalla de login, centrada y minimalista."""
    st.markdown("<div style='height:8vh;'></div>", unsafe_allow_html=True)
    col_left, col_center, col_right = st.columns([1, 1.1, 1])

    with col_center:
        logo_path = os.path.join("assets", "logo.png")
        st.markdown("<div style='text-align:center;'>", unsafe_allow_html=True)
        if os.path.exists(logo_path):
            st.image(logo_path, width=64)
        else:
            st.markdown("<div style='font-size:2.6rem;'>🗂️</div>", unsafe_allow_html=True)
        st.markdown(
            f"""
            <h2 style="text-align:center;margin-bottom:0;">{APP_NAME}</h2>
            <div style="text-align:center;color:#6B7280;margin-bottom:1.6rem;">{APP_TAGLINE}</div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

        with st.container():
            st.markdown("<div class='app-card scale-in'>", unsafe_allow_html=True)
            username = st.text_input("Usuario", placeholder="tu.usuario")
            password = st.text_input("Contraseña", type="password", placeholder="••••••••")
            st.markdown("<div style='height:0.4rem;'></div>", unsafe_allow_html=True)
            login_clicked = st.button("Iniciar sesión", type="primary", use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        if login_clicked:
            user = auth_service.login(username, password)
            if user:
                auth_service.set_current_user(user)
                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos.")


def render_app(auth_service: AuthService, account_service: AccountService) -> None:
    """Renderiza la aplicación autenticada con sidebar y enrutamiento de páginas."""
    selected_page = render_sidebar()

    toast_message = st.session_state.pop("toast_message", None)
    if toast_message:
        st.toast(toast_message, icon="✅")

    if selected_page == "Dashboard":
        dashboard.render(account_service)
    elif selected_page == "Hoy":
        hoy.render(account_service)
    elif selected_page == "Historial":
        historial.render(account_service)
    elif selected_page == "Configuración":
        configuracion.render()


def main() -> None:
    """Función principal: inyecta estilos y decide entre login o aplicación."""
    inject_global_styles()

    try:
        sheets_service = get_sheets_service()
    except Exception as exc:  # noqa: BLE001
        st.error(
            "No fue posible conectar con Google Sheets. Verifica las credenciales en "
            "`.streamlit/secrets.toml` y que la hoja haya sido compartida con el service account."
        )
        st.exception(exc)
        st.stop()

    auth_service = AuthService(sheets_service)
    account_service = AccountService(sheets_service)

    if not AuthService.is_authenticated():
        render_login(auth_service)
    else:
        render_app(auth_service, account_service)


if __name__ == "__main__":
    main()
