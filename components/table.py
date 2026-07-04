"""Tabla avanzada de cuentas creadas, basada en AgGrid."""

from io import BytesIO

import pandas as pd
import streamlit as st
from st_aggrid import AgGrid, ColumnsAutoSizeMode, DataReturnMode, GridOptionsBuilder, GridUpdateMode
from st_aggrid.shared import JsCode

from utils.constants import ACCOUNTS_HEADERS
from utils.helpers import truncate

DOUBLE_CLICK_JS = JsCode(
    """
    function(params) {
        const api = params.api;
        const newValue = Date.now();
        const updated = Object.assign({}, params.data, {_edit_trigger: newValue});
        api.applyTransaction({update: [updated]});
    }
    """
)

DISPLAY_COLUMNS = [c for c in ACCOUNTS_HEADERS if c not in ("Pass1", "Pass2")]


def render_accounts_table(df: pd.DataFrame, key: str = "accounts_grid") -> dict:
    """Renderiza la tabla principal de cuentas y devuelve el estado de selección/edición.

    El diccionario resultado contiene:
        - selected: dict de la fila seleccionada (o None)
        - edit_triggered_id: ID de la fila si se detectó doble clic
    """
    if df.empty:
        st.info("Aún no hay cuentas registradas. Crea la primera con el botón **+ Nueva cuenta**.")
        return {"selected": None, "edit_triggered_id": None}

    grid_df = df.copy()
    if "_edit_trigger" not in grid_df.columns:
        grid_df["_edit_trigger"] = 0
    display_df = grid_df[DISPLAY_COLUMNS + ["_edit_trigger"]].copy()
    display_df["Comentarios"] = display_df["Comentarios"].apply(lambda x: truncate(x, 60))

    builder = GridOptionsBuilder.from_dataframe(display_df)
    builder.configure_default_column(resizable=True, sortable=True, filter=True, editable=False, wrapText=False)
    builder.configure_selection(selection_mode="single", use_checkbox=False)
    builder.configure_pagination(paginated=True, paginationAutoPageSize=False, paginationPageSize=12)
    builder.configure_column("_edit_trigger", hide=True)
    builder.configure_column("ID", pinned="left", width=100)
    builder.configure_grid_options(onRowDoubleClicked=DOUBLE_CLICK_JS, domLayout="normal")

    grid_options = builder.build()

    response = AgGrid(
        display_df,
        gridOptions=grid_options,
        update_mode=GridUpdateMode.SELECTION_CHANGED | GridUpdateMode.MODEL_CHANGED,
        data_return_mode=DataReturnMode.AS_INPUT,
        columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS,
        fit_columns_on_grid_load=False,
        theme="alpine",
        height=430,
        allow_unsafe_jscode=True,
        key=key,
    )

    selected_rows = response.selected_rows
    selected = None
    if selected_rows is not None and len(selected_rows) > 0:
        if isinstance(selected_rows, pd.DataFrame):
            selected = selected_rows.iloc[0].to_dict()
        else:
            selected = selected_rows[0]

    edit_triggered_id = None
    returned_df = response.data
    if returned_df is not None and "_edit_trigger" in returned_df.columns:
        prev_triggers = st.session_state.get(f"{key}_triggers", {})
        new_triggers = dict(zip(returned_df["ID"], returned_df["_edit_trigger"]))
        for row_id, value in new_triggers.items():
            if value and value != prev_triggers.get(row_id, 0):
                edit_triggered_id = row_id
        st.session_state[f"{key}_triggers"] = new_triggers

    return {"selected": selected, "edit_triggered_id": edit_triggered_id}


def export_buttons(df: pd.DataFrame) -> None:
    """Renderiza botones de exportación a Excel y CSV."""
    export_df = df.drop(columns=["_edit_trigger"], errors="ignore")
    col_csv, col_xlsx = st.columns(2)
    with col_csv:
        st.download_button(
            "⬇️ Exportar CSV",
            data=export_df.to_csv(index=False).encode("utf-8"),
            file_name="cuentas.csv",
            mime="text/csv",
            use_container_width=True,
        )
    with col_xlsx:
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            export_df.to_excel(writer, index=False, sheet_name="Cuentas")
        st.download_button(
            "⬇️ Exportar Excel",
            data=buffer.getvalue(),
            file_name="cuentas.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )
