"""Página de Historial: consulta de registros por fecha con filtros."""

from datetime import date

import streamlit as st

from components.table import export_buttons, render_accounts_table
from services.accounts import AccountService
from utils.helpers import parse_date_safe


def render(account_service: AccountService) -> None:
    """Renderiza la página de historial con calendario y filtros."""
    st.title("Historial")
    st.markdown(
        "<div class='app-subtitle'>Consulta las cuentas creadas en cualquier fecha anterior.</div>",
        unsafe_allow_html=True,
    )

    df = account_service.list_accounts()

    col_date, col_emp, col_search = st.columns([1.2, 1.2, 2])
    with col_date:
        selected_date = st.date_input("Fecha", value=date.today())
    with col_emp:
        empleados = ["Todos"]
        if not df.empty and "Empleado" in df.columns:
            empleados += sorted([e for e in df["Empleado"].dropna().unique().tolist() if e])
        empleado_filtro = st.selectbox("Empleado", empleados)
    with col_search:
        busqueda = st.text_input("Buscar", placeholder="Buscar por email, nombre o usuario…")

    if df.empty:
        st.info("No hay registros disponibles todavía.")
        return

    filtered = df.copy()
    filtered["_fecha"] = filtered["Fecha"].apply(parse_date_safe)
    filtered = filtered[filtered["_fecha"] == selected_date]

    if empleado_filtro != "Todos":
        filtered = filtered[filtered["Empleado"] == empleado_filtro]

    if busqueda:
        term = busqueda.strip().lower()
        mask = (
            filtered["Email"].astype(str).str.lower().str.contains(term)
            | filtered["Nombre"].astype(str).str.lower().str.contains(term)
            | filtered["Usuario"].astype(str).str.lower().str.contains(term)
        )
        filtered = filtered[mask]

    filtered = filtered.drop(columns=["_fecha"], errors="ignore")

    st.markdown(f"**{len(filtered)}** registro(s) encontrados para el {selected_date.strftime('%d/%m/%Y')}.")

    render_accounts_table(filtered, key="historial_grid")

    if not filtered.empty:
        st.markdown("<div style='height:0.8rem;'></div>", unsafe_allow_html=True)
        export_buttons(filtered)
