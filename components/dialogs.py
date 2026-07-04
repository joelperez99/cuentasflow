"""Diálogos de confirmación reutilizables."""

import streamlit as st

from services.accounts import AccountService


@st.dialog("Eliminar cuenta")
def confirm_delete_dialog(account_service: AccountService, account_id: str, account_label: str) -> None:
    """Muestra un diálogo de confirmación antes de eliminar una cuenta."""
    st.markdown(f"¿Deseas eliminar la cuenta **{account_label}**? Esta acción no se puede deshacer.")
    col_cancel, col_confirm = st.columns(2)
    with col_cancel:
        if st.button("Cancelar", use_container_width=True):
            st.rerun()
    with col_confirm:
        if st.button("Sí, eliminar", type="primary", use_container_width=True):
            account_service.delete_account(account_id)
            st.session_state["toast_message"] = "Cuenta eliminada correctamente."
            st.session_state["confirm_delete_id"] = None
            st.rerun()
