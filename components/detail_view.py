"""Modal de solo lectura con el detalle completo de una cuenta."""

import streamlit as st


def _field(label: str, value) -> None:
    """Renderiza un par label/valor con el texto completo, sin truncar."""
    display_value = value if value not in (None, "", "nan") else "—"
    st.markdown(
        f"""
        <div style="margin-bottom:0.9rem;">
            <div style="font-size:0.72rem;color:#6B7280;text-transform:uppercase;
                        letter-spacing:0.04em;font-weight:600;">{label}</div>
            <div style="font-size:0.98rem;font-weight:600;color:#111827;
                        word-break:break-word;white-space:pre-wrap;">{display_value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


@st.dialog("Detalle de la cuenta")
def account_detail_modal(row: dict, session_key: str = "view_account_id") -> None:
    """Muestra todos los campos de una cuenta de forma clara, en un popup centrado."""
    nombre_completo = f"{row.get('Nombre', '')} {row.get('Apellido', '')}".strip()
    st.markdown(f"### {nombre_completo or 'Cuenta sin nombre'}")
    st.markdown(f"<span class='pill'>ID: {row.get('ID', '')}</span>", unsafe_allow_html=True)
    st.markdown("<div style='height:0.8rem;'></div>", unsafe_allow_html=True)

    col_left, col_right = st.columns(2)
    with col_left:
        _field("Email", row.get("Email"))
        _field("DOB", row.get("DOB"))
        _field("Pass 1", row.get("Pass1"))
        _field("Pass 2", row.get("Pass2"))
        _field("Dirección", row.get("Direccion"))
    with col_right:
        _field("Usuario", row.get("Usuario"))
        _field("Teléfono", row.get("Telefono"))
        _field("Fecha", row.get("Fecha"))
        _field("Hora", row.get("Hora"))
        _field("Empleado", row.get("Empleado"))

    st.markdown("---")
    _field("Comentarios", row.get("Comentarios"))

    if st.button("Cerrar", type="primary", use_container_width=True):
        st.session_state[session_key] = None
        st.rerun()
