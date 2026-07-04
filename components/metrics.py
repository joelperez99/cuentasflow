"""Tarjetas de métricas para el Dashboard."""

import streamlit as st


def metric_tile(label: str, value: str, delta: str | None = None) -> None:
    """Renderiza una tarjeta de métrica tipo Stripe/Vercel dashboard."""
    delta_html = ""
    if delta:
        delta_html = f"<div style='font-size:0.75rem;color:#16A34A;font-weight:600;margin-top:0.2rem;'>{delta}</div>"
    st.markdown(
        f"""
        <div class="metric-tile fade-in">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            {delta_html}
        </div>
        """,
        unsafe_allow_html=True,
    )
