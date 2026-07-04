"""Servicio de autenticación de usuarios contra la hoja 'Usuarios'."""

import hashlib
import logging

import pandas as pd
import streamlit as st

from database.google_sheet import GoogleSheetsService
from utils.constants import SESSION_USER_KEY, SHEET_USERS, USERS_HEADERS

logger = logging.getLogger(__name__)


class AuthService:
    """Maneja login, logout y la sesión del usuario autenticado."""

    def __init__(self, sheets: GoogleSheetsService) -> None:
        self._sheets = sheets

    @staticmethod
    def _hash(password: str) -> str:
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    def _load_users(self) -> pd.DataFrame:
        return self._sheets.read_all(SHEET_USERS, USERS_HEADERS)

    def login(self, username: str, password: str) -> dict | None:
        """Valida credenciales contra Google Sheets. Devuelve el usuario o None."""
        if not username or not password:
            return None
        users = self._load_users()
        if users.empty:
            return None
        match = users[users["Usuario"].astype(str).str.strip() == username.strip()]
        if match.empty:
            return None
        stored_password = str(match.iloc[0]["Password"])
        provided_hash = self._hash(password)
        if stored_password != password and stored_password != provided_hash:
            return None
        user = {
            "usuario": match.iloc[0]["Usuario"],
            "nombre": match.iloc[0].get("Nombre", match.iloc[0]["Usuario"]),
            "rol": match.iloc[0].get("Rol", "Empleado"),
        }
        return user

    @staticmethod
    def current_user() -> dict | None:
        """Devuelve el usuario en sesión, si existe."""
        return st.session_state.get(SESSION_USER_KEY)

    @staticmethod
    def set_current_user(user: dict) -> None:
        st.session_state[SESSION_USER_KEY] = user

    @staticmethod
    def logout() -> None:
        st.session_state.pop(SESSION_USER_KEY, None)

    @staticmethod
    def is_authenticated() -> bool:
        return SESSION_USER_KEY in st.session_state
