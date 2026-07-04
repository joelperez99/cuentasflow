"""Servicio de negocio para la gestión de cuentas creadas."""

import logging

import pandas as pd
import streamlit as st

from database.google_sheet import GoogleSheetsService
from utils.constants import ACCOUNTS_HEADERS, CACHE_TTL_SECONDS, SHEET_ACCOUNTS
from utils.helpers import generate_uuid, now_time_str, today_str

logger = logging.getLogger(__name__)


class AccountService:
    """Encapsula las reglas de negocio del CRUD de cuentas."""

    def __init__(self, sheets: GoogleSheetsService) -> None:
        self._sheets = sheets

    def list_accounts(self) -> pd.DataFrame:
        """Devuelve todas las cuentas registradas (cacheado brevemente)."""
        return _cached_read(self._sheets)

    def refresh(self) -> None:
        """Invalida la caché para forzar una relectura de Google Sheets."""
        _cached_read.clear()

    def email_exists_today(self, email: str, exclude_id: str | None = None) -> bool:
        """Verifica si un email ya fue registrado en el día de hoy."""
        df = self.list_accounts()
        if df.empty:
            return False
        today = today_str()
        mask = (df["Email"].astype(str).str.strip().str.lower() == email.strip().lower()) & (
            df["Fecha"].astype(str) == today
        )
        if exclude_id:
            mask &= df["ID"].astype(str) != str(exclude_id)
        return bool(mask.any())

    def create_account(self, data: dict, empleado: str) -> str:
        """Crea una nueva cuenta y la persiste en Google Sheets."""
        new_id = generate_uuid()
        row = {
            "ID": new_id,
            "Email": data.get("email", "").strip(),
            "DOB": data.get("dob", ""),
            "Pass1": data.get("pass1", ""),
            "Pass2": data.get("pass2", ""),
            "Direccion": data.get("direccion", ""),
            "Nombre": data.get("nombre", ""),
            "Apellido": data.get("apellido", ""),
            "Telefono": data.get("telefono", ""),
            "Usuario": data.get("usuario", ""),
            "Comentarios": data.get("comentarios", ""),
            "Fecha": today_str(),
            "Hora": now_time_str(),
            "Empleado": empleado,
        }
        self._sheets.append_row(SHEET_ACCOUNTS, ACCOUNTS_HEADERS, row)
        self.refresh()
        return new_id

    def update_account(self, account_id: str, data: dict, empleado: str | None = None) -> bool:
        """Actualiza una cuenta existente conservando fecha/hora originales."""
        df = self.list_accounts()
        existing = df[df["ID"].astype(str) == str(account_id)]
        if existing.empty:
            return False
        current = existing.iloc[0].to_dict()
        row = {
            "ID": account_id,
            "Email": data.get("email", current.get("Email", "")).strip(),
            "DOB": data.get("dob", current.get("DOB", "")),
            "Pass1": data.get("pass1", current.get("Pass1", "")),
            "Pass2": data.get("pass2", current.get("Pass2", "")),
            "Direccion": data.get("direccion", current.get("Direccion", "")),
            "Nombre": data.get("nombre", current.get("Nombre", "")),
            "Apellido": data.get("apellido", current.get("Apellido", "")),
            "Telefono": data.get("telefono", current.get("Telefono", "")),
            "Usuario": data.get("usuario", current.get("Usuario", "")),
            "Comentarios": data.get("comentarios", current.get("Comentarios", "")),
            "Fecha": current.get("Fecha", today_str()),
            "Hora": current.get("Hora", now_time_str()),
            "Empleado": empleado or current.get("Empleado", ""),
        }
        success = self._sheets.update_row(SHEET_ACCOUNTS, ACCOUNTS_HEADERS, "ID", account_id, row)
        if success:
            self.refresh()
        return success

    def delete_account(self, account_id: str) -> bool:
        """Elimina una cuenta por su ID."""
        success = self._sheets.delete_row(SHEET_ACCOUNTS, ACCOUNTS_HEADERS, "ID", account_id)
        if success:
            self.refresh()
        return success

    def duplicate_account(self, account_id: str, empleado: str) -> str | None:
        """Duplica una cuenta existente asignándole un nuevo ID y fecha/hora actuales."""
        df = self.list_accounts()
        existing = df[df["ID"].astype(str) == str(account_id)]
        if existing.empty:
            return None
        data = existing.iloc[0].to_dict()
        payload = {
            "email": data.get("Email", ""),
            "dob": data.get("DOB", ""),
            "pass1": data.get("Pass1", ""),
            "pass2": data.get("Pass2", ""),
            "direccion": data.get("Direccion", ""),
            "nombre": data.get("Nombre", ""),
            "apellido": data.get("Apellido", ""),
            "telefono": data.get("Telefono", ""),
            "usuario": data.get("Usuario", ""),
            "comentarios": data.get("Comentarios", ""),
        }
        return self.create_account(payload, empleado)


@st.cache_data(ttl=CACHE_TTL_SECONDS, show_spinner=False)
def _cached_read(_sheets: GoogleSheetsService) -> pd.DataFrame:
    """Lectura cacheada de la hoja de cuentas para minimizar llamadas a la API."""
    return _sheets.read_all(SHEET_ACCOUNTS, ACCOUNTS_HEADERS)
