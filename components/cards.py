"""Tarjetas informativas reutilizables (estilo Notion)."""

import streamlit as st


def info_banner(icon: str, text: str) -> None:
    """Renderiza el banner informativo con icono, usado en la página Hoy."""
    st.markdown(
        f"""
        <div class="info-banner">
            <div style="font-size:1.6rem;">{icon}</div>
            <div style="font-size:0.95rem;color:#166534;font-weight:500;">{text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def mini_card(label: str, value: str, icon: str = "") -> None:
    """Renderiza una tarjeta pequeña con label + valor, alineada horizontalmente."""
    st.markdown(
        f"""
        <div class="app-card fade-in" style="text-align:left;">
            <div style="font-size:0.75rem;color:#6B7280;text-transform:uppercase;
                        letter-spacing:0.04em;font-weight:600;">{icon} {label}</div>
            <div style="font-size:1.05rem;font-weight:700;margin-top:0.25rem;">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_title(title: str, subtitle: str = "") -> None:
    """Renderiza un título de sección consistente con espaciado amplio."""
    st.markdown(f"### {title}")
    if subtitle:
        st.markdown(f"<div class='app-subtitle'>{subtitle}</div>", unsafe_allow_html=True)
