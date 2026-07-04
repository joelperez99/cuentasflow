"""Página de Configuración: proyecto, empleado, logo y tema."""

import streamlit as st

from utils.constants import DEFAULT_PROJECTS


def render() -> None:
    """Renderiza la página de configuración de la aplicación."""
    st.title("Configuración")
    st.markdown(
        "<div class='app-subtitle'>Ajusta las preferencias generales de la aplicación.</div>",
        unsafe_allow_html=True,
    )

    st.markdown("#### Proyecto activo")
    proyecto = st.text_input(
        "Nombre del proyecto",
        value=st.session_state.get("config_proyecto", DEFAULT_PROJECTS[0]),
    )

    st.markdown("#### Empleado por defecto")
    user = st.session_state.get("auth_user", {})
    empleado = st.text_input("Nombre del empleado", value=st.session_state.get("config_empleado", user.get("nombre", "")))

    st.markdown("#### Logo de la aplicación")
    logo = st.file_uploader("Subir logo (PNG)", type=["png"])
    if logo is not None:
        st.image(logo, width=120)

    st.markdown("#### Tema")
    tema = st.selectbox(
        "Selecciona un tema",
        ["Claro (predeterminado)", "Oscuro (próximamente)"],
        index=0 if st.session_state.get("config_tema", "Claro (predeterminado)") == "Claro (predeterminado)" else 1,
    )

    st.markdown("<div style='height:0.8rem;'></div>", unsafe_allow_html=True)
    if st.button("Guardar cambios", type="primary"):
        st.session_state["config_proyecto"] = proyecto
        st.session_state["config_empleado"] = empleado
        st.session_state["config_tema"] = tema
        if logo is not None:
            st.session_state["config_logo"] = logo.getvalue()
        st.toast("Configuración guardada correctamente.", icon="✅")
