"""Funciones auxiliares reutilizables en toda la aplicación."""

import re
import uuid
from datetime import date, datetime, timedelta

from utils.constants import DATE_FORMAT, TIME_FORMAT

# Formatos aceptados al leer fechas provenientes de Google Sheets, además del
# formato propio de la app. Google Sheets reformatea el texto escrito por un
# humano según el formato de la celda/columna, así que aceptamos variantes
# comunes para que las filas pegadas manualmente también se detecten.
_KNOWN_DATE_FORMATS = [DATE_FORMAT, "%d/%m/%Y", "%Y-%m-%d", "%m/%d/%Y", "%d-%m-%Y", "%Y/%m/%d", "%d.%m.%Y"]


def generate_uuid() -> str:
    """Genera un identificador único corto para una nueva cuenta."""
    return str(uuid.uuid4())[:8]


def today_str() -> str:
    """Devuelve la fecha actual como texto YYYY-MM-DD."""
    return datetime.now().strftime(DATE_FORMAT)


def now_time_str() -> str:
    """Devuelve la hora actual como texto HH:MM:SS."""
    return datetime.now().strftime(TIME_FORMAT)


def is_valid_email(email: str) -> bool:
    """Valida el formato básico de un correo electrónico."""
    if not email:
        return False
    pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
    return re.match(pattern, email.strip()) is not None


def is_valid_phone(phone: str) -> bool:
    """Valida que el teléfono contenga solo dígitos, espacios, guiones o +."""
    if not phone:
        return False
    cleaned = phone.strip()
    return bool(re.match(r"^\+?[\d\s\-()]{6,20}$", cleaned)) and any(c.isdigit() for c in cleaned)


def is_valid_dob(dob_str: str) -> bool:
    """Valida que la fecha de nacimiento tenga un formato correcto y sea pasada."""
    if not dob_str:
        return False
    try:
        parsed = datetime.strptime(dob_str, DATE_FORMAT).date()
        return parsed < date.today()
    except ValueError:
        return False


def parse_date_safe(value, fmt: str = DATE_FORMAT):
    """Intenta parsear una fecha proveniente de Sheets, probando varios formatos.

    Acepta texto en el formato propio de la app, variantes comunes (ISO,
    MM/DD/YYYY, etc.) que Google Sheets puede aplicar al pegar datos, objetos
    date/datetime, y números de serie de fecha de Sheets/Excel.
    """
    if value is None or value == "":
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, (int, float)):
        try:
            return (datetime(1899, 12, 30) + timedelta(days=float(value))).date()
        except (OverflowError, ValueError, OSError):
            return None

    text = str(value).strip()
    if not text:
        return None

    candidates = [fmt] + [f for f in _KNOWN_DATE_FORMATS if f != fmt]
    for candidate in candidates:
        try:
            return datetime.strptime(text, candidate).date()
        except ValueError:
            continue
    return None


def truncate(text: str, length: int = 40) -> str:
    """Recorta un texto largo agregando puntos suspensivos."""
    if text is None:
        return ""
    text = str(text)
    return text if len(text) <= length else text[: length - 1] + "…"
