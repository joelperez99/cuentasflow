"""Barra superior con título de página y acción principal alineada a la derecha."""

import streamlit as st


def page_header(title: str, action_label: str | None = None, action_key: str = "header_action") -> bool:
    """Renderiza un encabezado de página con un botón de acción opcional a la derecha.

    Devuelve True si el botón de acción fue presionado en este ciclo.
    """
    col_title, col_action = st.columns([5, 1.4])
    with col_title:
        st.markdown(f"## {title}")
    clicked = False
    if action_label:
        with col_action:
            st.markdown("<div style='margin-top:0.6rem;'></div>", unsafe_allow_html=True)
            clicked = st.button(action_label, type="primary", use_container_width=True, key=action_key)
    return clicked
