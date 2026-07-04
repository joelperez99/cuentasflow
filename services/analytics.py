"""Servicio de estadísticas y agregaciones sobre las cuentas registradas."""

from datetime import date, timedelta

import pandas as pd

from utils.helpers import parse_date_safe, today_str


class AnalyticsService:
    """Calcula métricas y series de datos a partir del DataFrame de cuentas."""

    def __init__(self, df: pd.DataFrame) -> None:
        self._df = df.copy()
        if not self._df.empty:
            self._df["_fecha"] = self._df["Fecha"].apply(parse_date_safe)

    @property
    def is_empty(self) -> bool:
        return self._df.empty

    def count_today(self) -> int:
        if self.is_empty:
            return 0
        return int((self._df["Fecha"].astype(str) == today_str()).sum())

    def count_range(self, start: date, end: date) -> int:
        if self.is_empty:
            return 0
        mask = self._df["_fecha"].apply(lambda d: d is not None and start <= d <= end)
        return int(mask.sum())

    def count_week(self) -> int:
        today = date.today()
        start = today - timedelta(days=today.weekday())
        return self.count_range(start, today)

    def count_month(self) -> int:
        today = date.today()
        start = today.replace(day=1)
        return self.count_range(start, today)

    def daily_average(self, days: int = 30) -> float:
        if self.is_empty:
            return 0.0
        today = date.today()
        start = today - timedelta(days=days)
        total = self.count_range(start, today)
        return round(total / days, 1)

    def weekly_series(self, weeks: int = 8) -> pd.DataFrame:
        """Devuelve el número de cuentas creadas por semana en las últimas N semanas."""
        today = date.today()
        rows = []
        for i in range(weeks - 1, -1, -1):
            week_start = today - timedelta(days=today.weekday() + i * 7)
            week_end = week_start + timedelta(days=6)
            rows.append({"Semana": week_start.strftime("%d %b"), "Cuentas": self.count_range(week_start, week_end)})
        return pd.DataFrame(rows)

    def monthly_series(self, months: int = 6) -> pd.DataFrame:
        """Devuelve el número de cuentas creadas por mes en los últimos N meses."""
        today = date.today()
        rows = []
        cursor = today.replace(day=1)
        buckets = []
        for _ in range(months):
            buckets.append(cursor)
            prev_month = cursor.month - 1 or 12
            prev_year = cursor.year - 1 if cursor.month == 1 else cursor.year
            cursor = cursor.replace(year=prev_year, month=prev_month, day=1)
        for month_start in reversed(buckets):
            if month_start.month == 12:
                next_month = month_start.replace(year=month_start.year + 1, month=1)
            else:
                next_month = month_start.replace(month=month_start.month + 1)
            month_end = next_month - timedelta(days=1)
            rows.append(
                {"Mes": month_start.strftime("%b %Y"), "Cuentas": self.count_range(month_start, month_end)}
            )
        return pd.DataFrame(rows)

    def by_employee(self) -> pd.DataFrame:
        """Cuenta el total de cuentas creadas por empleado."""
        if self.is_empty or "Empleado" not in self._df.columns:
            return pd.DataFrame(columns=["Empleado", "Cuentas"])
        result = self._df.groupby("Empleado").size().reset_index(name="Cuentas")
        return result.sort_values("Cuentas", ascending=False)

    def latest(self, n: int = 8) -> pd.DataFrame:
        """Devuelve los últimos N registros ordenados por fecha/hora descendente."""
        if self.is_empty:
            return self._df
        sorted_df = self._df.sort_values(["Fecha", "Hora"], ascending=False)
        return sorted_df.drop(columns=["_fecha"], errors="ignore").head(n)
