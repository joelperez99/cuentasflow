"""Funciones auxiliares reutilizables en toda la aplicación."""

import re
import uuid
from datetime import date, datetime

from utils.constants import DATE_FORMAT, TIME_FORMAT


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


def parse_date_safe(value: str, fmt: str = DATE_FORMAT):
    """Intenta parsear una fecha, devuelve None si falla."""
    try:
        return datetime.strptime(value, fmt).date()
    except (ValueError, TypeError):
        return None


def truncate(text: str, length: int = 40) -> str:
    """Recorta un texto largo agregando puntos suspensivos."""
    if text is None:
        return ""
    text = str(text)
    return text if len(text) <= length else text[: length - 1] + "…"
