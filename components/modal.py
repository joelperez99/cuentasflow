"""Modal (pop-up) para crear/editar cuentas, con formulario de dos columnas."""

import streamlit as st

from services.accounts import AccountService
from utils.helpers import is_valid_dob, is_valid_email, is_valid_phone


def _empty_form() -> dict:
    return {
        "email": "",
        "dob": "",
        "pass1": "",
        "pass2": "",
        "direccion": "",
        "nombre": "",
        "apellido": "",
        "telefono": "",
        "usuario": "",
        "comentarios": "",
    }


@st.dialog("Nueva cuenta")
def account_modal(account_service: AccountService, empleado: str, existing: dict | None = None) -> None:
    """Renderiza el modal de creación/edición de una cuenta."""
    is_edit = existing is not None
    data = existing.copy() if existing else _empty_form()

    if is_edit:
        st.markdown("Actualiza los datos de la cuenta seleccionada.")
    else:
        st.markdown("Completa los datos de la cuenta creada durante tu jornada.")

    col_left, col_right = st.columns(2)

    with col_left:
        email = st.text_input("Email *", value=data.get("email") or data.get("Email", ""), placeholder="nombre@dominio.com")
        dob = st.text_input("Fecha de nacimiento (DD/MM/AAAA) *", value=data.get("dob") or data.get("DOB", ""), placeholder="14/05/1990")
        pass1 = st.text_input("Contraseña 1 *", value=data.get("pass1") or data.get("Pass1", ""), type="password")
        pass2 = st.text_input("Contraseña 2", value=data.get("pass2") or data.get("Pass2", ""), type="password")
        direccion = st.text_input("Dirección", value=data.get("direccion") or data.get("Direccion", ""), placeholder="Calle 123, Ciudad")

    with col_right:
        nombre = st.text_input("Nombre *", value=data.get("nombre") or data.get("Nombre", ""), placeholder="Juan")
        apellido = st.text_input("Apellido *", value=data.get("apellido") or data.get("Apellido", ""), placeholder="Pérez")
        telefono = st.text_input("Teléfono *", value=data.get("telefono") or data.get("Telefono", ""), placeholder="+52 555 123 4567")
        usuario = st.text_input("Usuario", value=data.get("usuario") or data.get("Usuario", ""), placeholder="juan.perez")
        comentarios = st.text_area("Comentarios", value=data.get("comentarios") or data.get("Comentarios", ""), placeholder="Notas adicionales…", height=88)

    st.markdown("<div style='height:0.4rem;'></div>", unsafe_allow_html=True)
    col_cancel, col_save = st.columns(2)

    with col_cancel:
        if st.button("Cancelar", use_container_width=True):
            st.rerun()

    with col_save:
        save_label = "Guardar cambios" if is_edit else "Guardar"
        if st.button(save_label, type="primary", use_container_width=True):
            errors = []
            if not is_valid_email(email):
                errors.append("El email no tiene un formato válido.")
            if not is_valid_dob(dob):
                errors.append("La fecha de nacimiento debe tener formato DD/MM/AAAA y ser una fecha pasada.")
            if not pass1:
                errors.append("La contraseña 1 es obligatoria.")
            if not nombre.strip():
                errors.append("El nombre es obligatorio.")
            if not apellido.strip():
                errors.append("El apellido es obligatorio.")
            if not is_valid_phone(telefono):
                errors.append("El teléfono debe contener solo números y un formato válido.")

            exclude_id = existing.get("ID") if is_edit else None
            if not errors and account_service.email_exists_today(email, exclude_id=exclude_id):
                errors.append("Ya existe una cuenta con este email registrada hoy.")

            if errors:
                for err in errors:
                    st.error(err)
                return

            payload = {
                "email": email,
                "dob": dob,
                "pass1": pass1,
                "pass2": pass2,
                "direccion": direccion,
                "nombre": nombre,
                "apellido": apellido,
                "telefono": telefono,
                "usuario": usuario,
                "comentarios": comentarios,
            }

            if is_edit:
                account_service.update_account(existing.get("ID"), payload, empleado)
                st.session_state["toast_message"] = "Cuenta actualizada correctamente."
            else:
                account_service.create_account(payload, empleado)
                st.session_state["toast_message"] = "Cuenta creada correctamente."

            st.session_state["show_account_modal"] = False
            st.session_state["edit_account_data"] = None
            st.rerun()
