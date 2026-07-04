"""Página 'Hoy': registro diario de cuentas creadas."""

from datetime import datetime

import streamlit as st

from components.cards import info_banner, mini_card
from components.dialogs import confirm_delete_dialog
from components.modal import account_modal
from components.navbar import page_header
from components.table import export_buttons, render_accounts_table
from services.accounts import AccountService
from services.auth import AuthService
from utils.constants import DEFAULT_PROJECTS


def render(account_service: AccountService) -> None:
    """Renderiza la página de registro diario de cuentas."""
    user = AuthService.current_user()
    empleado = user.get("nombre", "Empleado") if user else "Empleado"

    st.title("¿Qué hice en el trabajo hoy?")
    info_banner(
        "💡",
        "Usa esta página todos los días para registrar las cuentas creadas durante tu jornada laboral.",
    )

    now = datetime.now()
    proyecto = st.session_state.get("config_proyecto", DEFAULT_PROJECTS[0])

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        mini_card("Fecha", now.strftime("%d/%m/%Y"), "📅")
    with col2:
        mini_card("Hora", now.strftime("%H:%M"), "⏰")
    with col3:
        mini_card("Empleado", empleado, "👤")
    with col4:
        mini_card("Proyecto", proyecto, "📁")
    with col5:
        mini_card("Estado", "Activo", "🟢")

    st.markdown("<div style='height:1.4rem;'></div>", unsafe_allow_html=True)

    clicked_new = page_header("Cuentas creadas", action_label="+ Nueva cuenta", action_key="new_account_btn")
    if clicked_new:
        st.session_state["edit_account_data"] = None
        st.session_state["show_account_modal"] = True

    df = account_service.list_accounts()
    result = render_accounts_table(df, key="hoy_grid")
    selected = result["selected"]
    edit_id = result["edit_triggered_id"]

    action_cols = st.columns(4)
    with action_cols[0]:
        if st.button("✏️ Editar seleccionada", use_container_width=True, disabled=selected is None):
            st.session_state["edit_account_data"] = selected
            st.session_state["show_account_modal"] = True
    with action_cols[1]:
        if st.button("📄 Duplicar seleccionada", use_container_width=True, disabled=selected is None):
            account_service.duplicate_account(selected["ID"], empleado)
            st.session_state["toast_message"] = "Cuenta duplicada correctamente."
            st.rerun()
    with action_cols[2]:
        if st.button("🗑️ Eliminar seleccionada", use_container_width=True, disabled=selected is None):
            st.session_state["confirm_delete_id"] = selected["ID"] if selected else None
    with action_cols[3]:
        pass

    if not df.empty:
        st.markdown("<div style='height:0.8rem;'></div>", unsafe_allow_html=True)
        export_buttons(df)

    if edit_id:
        matches = df[df["ID"].astype(str) == str(edit_id)]
        if not matches.empty:
            st.session_state["edit_account_data"] = matches.iloc[0].to_dict()
            st.session_state["show_account_modal"] = True

    if st.session_state.get("show_account_modal"):
        account_modal(account_service, empleado, existing=st.session_state.get("edit_account_data"))

    if st.session_state.get("confirm_delete_id"):
        acc_id = st.session_state["confirm_delete_id"]
        row = df[df["ID"].astype(str) == str(acc_id)]
        label = row.iloc[0]["Email"] if not row.empty else acc_id
        confirm_delete_dialog(account_service, acc_id, label)
