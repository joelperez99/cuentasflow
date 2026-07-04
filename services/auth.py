"""Servicio de autenticación de usuarios contra la hoja 'Usuarios'."""

import hashlib
import logging

import pandas as pd
import streamlit as st

from database.google_sheet import GoogleSheetsService
from utils.constants import (
    SESSION_TOKEN_PARAM,
    SESSION_USER_KEY,
    SESSION_USER_PARAM,
    SHEET_USERS,
    USERS_HEADERS,
)

logger = logging.getLogger(__name__)


class AuthService:
    """Maneja login, logout y la persistencia de la sesión del usuario autenticado.

    La sesión se guarda en `st.session_state` para el ciclo de vida normal de la app,
    y además se refleja en los parámetros de la URL (usuario + token firmado) para que
    un refresh del navegador no obligue a iniciar sesión de nuevo.
    """

    def __init__(self, sheets: GoogleSheetsService) -> None:
        self._sheets = sheets

    @staticmethod
    def _hash(password: str) -> str:
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    @staticmethod
    def _session_secret() -> str:
        """Clave usada para firmar el token de sesión persistido en la URL."""
        auth_secrets = st.secrets.get("auth", {})
        return auth_secrets.get("session_secret") or str(
            st.secrets.get("google_sheets", {}).get("spreadsheet_id", "cuentasflow-default-secret")
        )

    @classmethod
    def _session_token(cls, username: str) -> str:
        payload = f"{username}:{cls._session_secret()}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:24]

    def _load_users(self) -> pd.DataFrame:
        return self._sheets.read_all(SHEET_USERS, USERS_HEADERS)

    def _find_user(self, username: str) -> dict | None:
        users = self._load_users()
        if users.empty:
            return None
        match = users[users["Usuario"].astype(str).str.strip() == username.strip()]
        if match.empty:
            return None
        return {
            "usuario": match.iloc[0]["Usuario"],
            "nombre": match.iloc[0].get("Nombre", match.iloc[0]["Usuario"]),
            "rol": match.iloc[0].get("Rol", "Empleado"),
        }

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
        return {
            "usuario": match.iloc[0]["Usuario"],
            "nombre": match.iloc[0].get("Nombre", match.iloc[0]["Usuario"]),
            "rol": match.iloc[0].get("Rol", "Empleado"),
        }

    def restore_session(self) -> None:
        """Restaura la sesión desde los parámetros de la URL tras un refresh del navegador."""
        if self.is_authenticated():
            return
        params = st.query_params
        username = params.get(SESSION_USER_PARAM)
        token = params.get(SESSION_TOKEN_PARAM)
        if not username or not token:
            return
        if token != self._session_token(username):
            return
        user = self._find_user(username)
        if user:
            st.session_state[SESSION_USER_KEY] = user

    @staticmethod
    def current_user() -> dict | None:
        """Devuelve el usuario en sesión, si existe."""
        return st.session_state.get(SESSION_USER_KEY)

    @classmethod
    def set_current_user(cls, user: dict) -> None:
        """Guarda el usuario en sesión y persiste la sesión en la URL."""
        st.session_state[SESSION_USER_KEY] = user
        st.query_params[SESSION_USER_PARAM] = user["usuario"]
        st.query_params[SESSION_TOKEN_PARAM] = cls._session_token(user["usuario"])

    @staticmethod
    def logout() -> None:
        st.session_state.pop(SESSION_USER_KEY, None)
        st.query_params.pop(SESSION_USER_PARAM, None)
        st.query_params.pop(SESSION_TOKEN_PARAM, None)

    @staticmethod
    def is_authenticated() -> bool:
        return SESSION_USER_KEY in st.session_state
