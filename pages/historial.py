"""Página de Historial: calendario visual y tabla con filtros."""

import streamlit as st

from components.calendar_view import render_month_calendar
from components.detail_view import account_detail_modal
from components.table import export_buttons, render_accounts_table
from services.accounts import AccountService
from utils.helpers import parse_date_safe


def _apply_filters(df, empleado_filtro: str, busqueda: str):
    filtered = df.copy()
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
    return filtered


def _employee_options(df) -> list[str]:
    empleados = ["Todos"]
    if not df.empty and "Empleado" in df.columns:
        empleados += sorted([e for e in df["Empleado"].dropna().unique().tolist() if e])
    return empleados


def render(account_service: AccountService) -> None:
    """Renderiza la página de historial con calendario y tabla."""
    st.title("Historial")
    st.markdown(
        "<div class='app-subtitle'>Consulta las cuentas creadas en cualquier fecha anterior.</div>",
        unsafe_allow_html=True,
    )

    df = account_service.list_accounts()

    if df.empty:
        st.info("No hay registros disponibles todavía.")
        return

    tab_calendario, tab_tabla = st.tabs(["📅 Calendario", "📋 Tabla"])

    with tab_calendario:
        col_cal, col_filters = st.columns([1.3, 1])
        with col_cal:
            selected_date = render_month_calendar(df, key="historial_calendar")
        with col_filters:
            st.markdown("<div style='height:0.2rem;'></div>", unsafe_allow_html=True)
            empleado_filtro = st.selectbox("Empleado", _employee_options(df), key="cal_empleado")
            busqueda = st.text_input("Buscar", placeholder="Email, nombre o usuario…", key="cal_busqueda")

        parsed = df["Fecha"].apply(parse_date_safe)
        day_df = df[parsed == selected_date].copy()
        day_df = _apply_filters(day_df, empleado_filtro, busqueda)

        st.markdown("<div style='height:0.6rem;'></div>", unsafe_allow_html=True)
        st.markdown(
            f"**{len(day_df)}** cuenta(s) creada(s) el **{selected_date.strftime('%d/%m/%Y')}**."
        )
        cal_result = render_accounts_table(day_df, key="historial_calendar_grid")
        cal_selected = cal_result["selected"]
        if st.button(
            "👁️ Ver detalle", disabled=cal_selected is None, key="ver_detalle_calendario"
        ):
            st.session_state["view_account_id_cal"] = cal_selected["ID"] if cal_selected else None
        if not day_df.empty:
            st.markdown("<div style='height:0.8rem;'></div>", unsafe_allow_html=True)
            export_buttons(day_df, key="export_calendario")

    view_id_cal = st.session_state.get("view_account_id_cal")
    if view_id_cal:
        matches = df[df["ID"].astype(str) == str(view_id_cal)]
        if not matches.empty:
            account_detail_modal(matches.iloc[0].to_dict(), session_key="view_account_id_cal")
        else:
            st.session_state["view_account_id_cal"] = None

    with tab_tabla:
        col_emp, col_search = st.columns([1.2, 2])
        with col_emp:
            empleado_filtro_tabla = st.selectbox("Empleado", _employee_options(df), key="tabla_empleado")
        with col_search:
            busqueda_tabla = st.text_input(
                "Buscar", placeholder="Buscar por email, nombre o usuario…", key="tabla_busqueda"
            )

        filtered = _apply_filters(df, empleado_filtro_tabla, busqueda_tabla)
        st.markdown(f"**{len(filtered)}** registro(s) encontrados en total.")
        tabla_result = render_accounts_table(filtered, key="historial_tabla_grid")
        tabla_selected = tabla_result["selected"]
        if st.button(
            "👁️ Ver detalle", disabled=tabla_selected is None, key="ver_detalle_tabla"
        ):
            st.session_state["view_account_id_tabla"] = tabla_selected["ID"] if tabla_selected else None
        if not filtered.empty:
            st.markdown("<div style='height:0.8rem;'></div>", unsafe_allow_html=True)
            export_buttons(filtered, key="export_tabla")

    view_id_tabla = st.session_state.get("view_account_id_tabla")
    if view_id_tabla:
        matches = df[df["ID"].astype(str) == str(view_id_tabla)]
        if not matches.empty:
            account_detail_modal(matches.iloc[0].to_dict(), session_key="view_account_id_tabla")
        else:
            st.session_state["view_account_id_tabla"] = None
