"""Página de Dashboard con métricas y gráficas."""

import plotly.express as px
import streamlit as st

from components.cards import section_title
from components.metrics import metric_tile
from services.accounts import AccountService
from services.analytics import AnalyticsService
from utils.constants import COLOR_PRIMARY


def render(account_service: AccountService) -> None:
    """Renderiza el dashboard de estadísticas."""
    st.title("Dashboard")
    st.markdown(
        "<div class='app-subtitle'>Resumen de la actividad de registro de cuentas.</div>",
        unsafe_allow_html=True,
    )

    df = account_service.list_accounts()
    analytics = AnalyticsService(df)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        metric_tile("Cuentas hoy", str(analytics.count_today()))
    with col2:
        metric_tile("Esta semana", str(analytics.count_week()))
    with col3:
        metric_tile("Este mes", str(analytics.count_month()))
    with col4:
        metric_tile("Promedio diario", str(analytics.daily_average()))

    st.markdown("<div style='height:1.2rem;'></div>", unsafe_allow_html=True)

    if analytics.is_empty:
        st.info("Aún no hay datos suficientes para generar gráficas. Registra tu primera cuenta en la página **Hoy**.")
        return

    col_left, col_right = st.columns(2)

    with col_left:
        section_title("Cuentas por semana")
        weekly = analytics.weekly_series()
        fig_week = px.bar(weekly, x="Semana", y="Cuentas", color_discrete_sequence=[COLOR_PRIMARY])
        fig_week.update_layout(
            plot_bgcolor="white",
            paper_bgcolor="white",
            margin=dict(l=10, r=10, t=10, b=10),
            font_family="Inter",
        )
        st.plotly_chart(fig_week, use_container_width=True)

    with col_right:
        section_title("Cuentas por mes")
        monthly = analytics.monthly_series()
        fig_month = px.line(monthly, x="Mes", y="Cuentas", markers=True, color_discrete_sequence=[COLOR_PRIMARY])
        fig_month.update_layout(
            plot_bgcolor="white",
            paper_bgcolor="white",
            margin=dict(l=10, r=10, t=10, b=10),
            font_family="Inter",
        )
        st.plotly_chart(fig_month, use_container_width=True)

    section_title("Cuentas por empleado")
    by_employee = analytics.by_employee()
    if not by_employee.empty:
        fig_emp = px.bar(
            by_employee, x="Empleado", y="Cuentas", color_discrete_sequence=[COLOR_PRIMARY], orientation="v"
        )
        fig_emp.update_layout(
            plot_bgcolor="white",
            paper_bgcolor="white",
            margin=dict(l=10, r=10, t=10, b=10),
            font_family="Inter",
        )
        st.plotly_chart(fig_emp, use_container_width=True)

    section_title("Últimos registros")
    latest = analytics.latest(8)
    st.dataframe(
        latest[["Fecha", "Hora", "Email", "Nombre", "Apellido", "Empleado"]],
        use_container_width=True,
        hide_index=True,
    )
