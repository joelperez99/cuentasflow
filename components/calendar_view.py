"""Calendario mensual visual para la página de Historial, estilo Notion."""

import calendar as cal
from datetime import date

import pandas as pd
import streamlit as st

from utils.helpers import parse_date_safe

WEEKDAY_LABELS = ["Dom", "Lun", "Mar", "Mié", "Jue", "Vie", "Sáb"]


def _counts_by_day(df: pd.DataFrame, year: int, month: int) -> dict[int, int]:
    """Cuenta cuántas cuentas se crearon por cada día del mes indicado."""
    if df.empty:
        return {}
    parsed = df["Fecha"].apply(parse_date_safe)
    mask = parsed.apply(lambda d: d is not None and d.year == year and d.month == month)
    days = parsed[mask].apply(lambda d: d.day)
    return days.value_counts().to_dict()


def render_month_calendar(df: pd.DataFrame, key: str = "calendar") -> date:
    """Renderiza un calendario mensual navegable y devuelve la fecha seleccionada."""
    today = date.today()
    month_key = f"{key}_month"
    selected_key = f"{key}_selected_date"

    if month_key not in st.session_state:
        st.session_state[month_key] = date(today.year, today.month, 1)
    if selected_key not in st.session_state:
        st.session_state[selected_key] = today

    current_month: date = st.session_state[month_key]
    selected_date: date = st.session_state[selected_key]

    counts = _counts_by_day(df, current_month.year, current_month.month)

    col_prev, col_title, col_today, col_next = st.columns([1, 4, 1.4, 1])
    with col_prev:
        if st.button("◀", key=f"{key}_prev", use_container_width=True):
            prev_month = current_month.month - 1 or 12
            prev_year = current_month.year - 1 if current_month.month == 1 else current_month.year
            st.session_state[month_key] = date(prev_year, prev_month, 1)
            st.rerun()
    with col_title:
        st.markdown(
            f"<div style='text-align:center;font-weight:700;font-size:1.1rem;padding-top:0.3rem;'>"
            f"{current_month.strftime('%B %Y').capitalize()}</div>",
            unsafe_allow_html=True,
        )
    with col_today:
        if st.button("Hoy", key=f"{key}_today", use_container_width=True):
            st.session_state[month_key] = date(today.year, today.month, 1)
            st.session_state[selected_key] = today
            st.rerun()
    with col_next:
        if st.button("▶", key=f"{key}_next", use_container_width=True):
            next_month = current_month.month + 1 if current_month.month < 12 else 1
            next_year = current_month.year + 1 if current_month.month == 12 else current_month.year
            st.session_state[month_key] = date(next_year, next_month, 1)
            st.rerun()

    st.markdown("<div style='height:0.4rem;'></div>", unsafe_allow_html=True)

    header_cols = st.columns(7)
    for col, label in zip(header_cols, WEEKDAY_LABELS):
        col.markdown(
            f"<div style='text-align:center;font-size:0.75rem;color:#6B7280;font-weight:600;'>{label}</div>",
            unsafe_allow_html=True,
        )

    weeks = cal.Calendar(firstweekday=6).monthdayscalendar(current_month.year, current_month.month)

    for week in weeks:
        week_cols = st.columns(7)
        for col, day in zip(week_cols, week):
            if day == 0:
                col.markdown("<div style='height:52px;'></div>", unsafe_allow_html=True)
                continue
            day_date = date(current_month.year, current_month.month, day)
            count = counts.get(day, 0)
            label = f"{day} · {count}" if count else str(day)
            is_today = day_date == today
            is_selected = day_date == selected_date
            button_type = "primary" if is_selected else "secondary"
            with col:
                if st.button(
                    label,
                    key=f"{key}_day_{current_month.year}_{current_month.month}_{day}",
                    use_container_width=True,
                    type=button_type,
                    help="Hoy" if is_today else None,
                ):
                    st.session_state[selected_key] = day_date
                    st.rerun()

    return st.session_state[selected_key]
