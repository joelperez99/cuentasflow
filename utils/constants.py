"""Constantes globales de la aplicación."""

APP_NAME = "CuentasFlow"
APP_TAGLINE = "Registro diario de cuentas"

# --- Google Sheets ---
SHEET_USERS = "Usuarios"
SHEET_ACCOUNTS = "Cuentas"
SHEET_CONFIG = "Configuracion"

USERS_HEADERS = ["Usuario", "Password", "Nombre", "Rol"]

ACCOUNTS_HEADERS = [
    "ID",
    "Email",
    "DOB",
    "Pass1",
    "Pass2",
    "Direccion",
    "Nombre",
    "Apellido",
    "Telefono",
    "Usuario",
    "Comentarios",
    "Fecha",
    "Hora",
    "Empleado",
]

CONFIG_HEADERS = ["Clave", "Valor"]

# --- Paleta de colores (estilo SaaS) ---
COLOR_BG = "#FAFAFA"
COLOR_CARD = "#FFFFFF"
COLOR_BORDER = "#E5E7EB"
COLOR_PRIMARY = "#22C55E"
COLOR_PRIMARY_HOVER = "#16A34A"
COLOR_TEXT = "#111827"
COLOR_TEXT_SECONDARY = "#6B7280"
COLOR_DANGER = "#EF4444"
COLOR_DANGER_HOVER = "#DC2626"

# --- Sesión ---
SESSION_USER_KEY = "auth_user"
SESSION_PAGE_KEY = "current_page"
SESSION_USER_PARAM = "u"
SESSION_TOKEN_PARAM = "t"

# --- Cache ---
CACHE_TTL_SECONDS = 30

DATE_FORMAT = "%d/%m/%Y"
TIME_FORMAT = "%H:%M:%S"
DOB_FORMAT = "%d/%m/%Y"

DEFAULT_PROJECTS = ["Proyecto General"]
DEFAULT_EMPLOYEES = []
