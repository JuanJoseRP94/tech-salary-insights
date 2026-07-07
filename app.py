"""
app.py
Dashboard interactivo de salarios en el sector tech.

Ejecutar con: streamlit run app.py
"""

import sys
import os

import streamlit as st

# Permite importar los módulos de src/ sin instalarlos como paquete.
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from data_loader import load_salaries  # noqa: E402
from visualizations import (  # noqa: E402
    fig_salary_by_experience,
    fig_top_job_titles,
    fig_remote_vs_salary,
    fig_salary_trend,
    fig_company_size_comparison,
)

st.set_page_config(
    page_title="Tech Salary Insights",
    page_icon="💼",
    layout="wide",
)


@st.cache_data
def get_data():
    return load_salaries("data/salaries.csv")


def main():
    st.title("💼 Tech Salary Insights")
    st.caption(
        "Análisis interactivo de más de 149.000 salarios reales en tecnología, "
        "IA/ML y datos (2023-2025). Fuente: aijobs.net (dominio público)."
    )

    df = get_data()

    # --- Filtros en la barra lateral ---
    st.sidebar.header("Filtros")

    years = sorted(df["work_year"].unique())
    selected_years = st.sidebar.multiselect("Año", years, default=years)

    experience_options = ["Junior (Entry-level)", "Mid-level", "Senior", "Executive"]
    selected_experience = st.sidebar.multiselect(
        "Nivel de experiencia", experience_options, default=experience_options
    )

    company_size_options = df["company_size_label"].dropna().unique().tolist()
    selected_company_size = st.sidebar.multiselect(
        "Tamaño de empresa", company_size_options, default=company_size_options
    )

    filtered_df = df[
        df["work_year"].isin(selected_years)
        & df["experience_label"].isin(selected_experience)
        & df["company_size_label"].isin(selected_company_size)
    ]

    if filtered_df.empty:
        st.warning("No hay datos para los filtros seleccionados. Prueba a ampliar la selección.")
        return

    # --- KPIs ---
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Registros analizados", f"{len(filtered_df):,}")
    col2.metric("Salario medio", f"${filtered_df['salary_in_usd'].mean():,.0f}")
    col3.metric("Salario mediano", f"${filtered_df['salary_in_usd'].median():,.0f}")
    col4.metric(
        "% Trabajo 100% remoto",
        f"{(filtered_df['remote_ratio'] == 100).mean() * 100:.0f}%",
    )

    st.divider()

    # --- Gráficas ---
    col_left, col_right = st.columns(2)
    with col_left:
        st.plotly_chart(fig_salary_by_experience(filtered_df), use_container_width=True)
    with col_right:
        st.plotly_chart(fig_company_size_comparison(filtered_df), use_container_width=True)

    col_left2, col_right2 = st.columns(2)
    with col_left2:
        st.plotly_chart(fig_remote_vs_salary(filtered_df), use_container_width=True)
    with col_right2:
        st.plotly_chart(fig_salary_trend(filtered_df), use_container_width=True)

    st.plotly_chart(fig_top_job_titles(filtered_df), use_container_width=True)

    with st.expander("Ver datos en bruto"):
        st.dataframe(filtered_df, use_container_width=True)


if __name__ == "__main__":
    main()