"""Capa de acceso a Google Sheets, único almacenamiento de la aplicación."""

import logging
import time
from typing import Any

import gspread
import pandas as pd
import streamlit as st
from google.oauth2.service_account import Credentials
from gspread.exceptions import APIError, WorksheetNotFound

from utils.constants import (
    ACCOUNTS_HEADERS,
    CONFIG_HEADERS,
    SHEET_ACCOUNTS,
    SHEET_CONFIG,
    SHEET_USERS,
    USERS_HEADERS,
)

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


class GoogleSheetsService:
    """Encapsula toda la comunicación con Google Sheets.

    Se encarga de: autenticación, creación automática de hojas/encabezados,
    reconexión ante errores transitorios y operaciones CRUD genéricas.
    """

    def __init__(self) -> None:
        self._client: gspread.Client | None = None
        self._spreadsheet: gspread.Spreadsheet | None = None
        self._connect()

    # ------------------------------------------------------------------ #
    # Conexión
    # ------------------------------------------------------------------ #
    def _connect(self) -> None:
        """Crea el cliente gspread a partir de las credenciales en secrets.toml."""
        try:
            creds_info = dict(st.secrets["gcp_service_account"])
            credentials = Credentials.from_service_account_info(creds_info, scopes=SCOPES)
            self._client = gspread.authorize(credentials)
            sheet_id = st.secrets["google_sheets"]["spreadsheet_id"]
            self._spreadsheet = self._client.open_by_key(sheet_id)
            logger.info("Conexión establecida con Google Sheets.")
        except Exception:
            logger.exception("Error al conectar con Google Sheets.")
            raise

    def _with_retry(self, func, *args, retries: int = 3, **kwargs) -> Any:
        """Ejecuta una llamada a la API reintentando ante errores transitorios."""
        last_error = None
        for attempt in range(retries):
            try:
                return func(*args, **kwargs)
            except APIError as exc:
                last_error = exc
                logger.warning("APIError intento %s/%s: %s", attempt + 1, retries, exc)
                time.sleep(1.2 * (attempt + 1))
                if attempt == retries - 1:
                    continue
                self._connect()
        logger.error("Fallo definitivo tras %s reintentos.", retries)
        raise last_error

    def _get_or_create_worksheet(self, name: str, headers: list[str]) -> gspread.Worksheet:
        """Obtiene una hoja o la crea con sus encabezados si no existe."""
        try:
            worksheet = self._spreadsheet.worksheet(name)
        except WorksheetNotFound:
            logger.info("Hoja '%s' no encontrada, creando…", name)
            worksheet = self._spreadsheet.add_worksheet(title=name, rows=1000, cols=len(headers) + 2)
            worksheet.append_row(headers)
        existing_headers = worksheet.row_values(1)
        if existing_headers != headers:
            if not existing_headers:
                worksheet.append_row(headers)
        return worksheet

    def ensure_schema(self) -> None:
        """Asegura que las hojas Usuarios, Cuentas y Configuracion existan."""
        self._get_or_create_worksheet(SHEET_USERS, USERS_HEADERS)
        self._get_or_create_worksheet(SHEET_ACCOUNTS, ACCOUNTS_HEADERS)
        self._get_or_create_worksheet(SHEET_CONFIG, CONFIG_HEADERS)

    # ------------------------------------------------------------------ #
    # Operaciones genéricas
    # ------------------------------------------------------------------ #
    def read_all(self, sheet_name: str, headers: list[str]) -> pd.DataFrame:
        """Lee todos los registros de una hoja como DataFrame."""
        worksheet = self._get_or_create_worksheet(sheet_name, headers)
        records = self._with_retry(worksheet.get_all_records)
        if not records:
            return pd.DataFrame(columns=headers)
        return pd.DataFrame(records)

    def append_row(self, sheet_name: str, headers: list[str], row: dict) -> None:
        """Agrega una fila nueva al final de la hoja."""
        worksheet = self._get_or_create_worksheet(sheet_name, headers)
        values = [row.get(h, "") for h in headers]
        self._with_retry(worksheet.append_row, values, value_input_option="RAW")

    def update_row(self, sheet_name: str, headers: list[str], id_column: str, id_value: str, row: dict) -> bool:
        """Actualiza la fila cuyo id_column coincide con id_value."""
        worksheet = self._get_or_create_worksheet(sheet_name, headers)
        cell = self._with_retry(worksheet.find, str(id_value))
        if cell is None:
            return False
        col_index = headers.index(id_column)
        if cell.col != col_index + 1:
            all_ids = self._with_retry(worksheet.col_values, col_index + 1)
            try:
                row_number = all_ids.index(str(id_value)) + 1
            except ValueError:
                return False
        else:
            row_number = cell.row
        values = [row.get(h, "") for h in headers]
        last_cell = gspread.utils.rowcol_to_a1(row_number, len(headers))
        self._with_retry(
            worksheet.update,
            f"A{row_number}:{last_cell}",
            [values],
            value_input_option="RAW",
        )
        return True

    def delete_row(self, sheet_name: str, headers: list[str], id_column: str, id_value: str) -> bool:
        """Elimina la fila cuyo id_column coincide con id_value."""
        worksheet = self._get_or_create_worksheet(sheet_name, headers)
        col_index = headers.index(id_column)
        all_ids = self._with_retry(worksheet.col_values, col_index + 1)
        try:
            row_number = all_ids.index(str(id_value)) + 1
        except ValueError:
            return False
        self._with_retry(worksheet.delete_rows, row_number)
        return True


@st.cache_resource(show_spinner=False)
def get_sheets_service() -> GoogleSheetsService:
    """Devuelve una instancia única (cacheada) del servicio de Google Sheets."""
    service = GoogleSheetsService()
    service.ensure_schema()
    return service
