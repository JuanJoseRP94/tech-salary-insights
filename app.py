"""
app.py
Dashboard interactivo de salarios en el sector tech.

Ejecutar con: streamlit run app.py
"""

import sys
import os
from dotenv import load_dotenv
load_dotenv()
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
from llm_insights import ask_question  # noqa: E402


def get_groq_api_key():
    """
    Busca la API key de Groq primero en st.secrets (usado en Streamlit Cloud),
    y si no existe, en variables de entorno (usado en desarrollo local con .env).
    Devuelve None si no se encuentra en ningún sitio.
    """
    try:
        return st.secrets["GROQ_API_KEY"]
    except (KeyError, FileNotFoundError):
        return os.environ.get("GROQ_API_KEY")

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

    st.divider()

    # --- Sección de IA generativa: "Pregunta a tus datos" ---
    st.subheader("🤖 Pregunta a tus datos")
    st.caption(
        "Escribe una pregunta en lenguaje natural sobre los datos filtrados "
        "arriba. Un modelo de IA generativa (Llama 3.3 vía Groq) analizará el "
        "resumen estadístico real y te responderá."
    )

    api_key = get_groq_api_key()

    if not api_key:
        st.info(
            "Esta función necesita una clave gratuita de Groq. "
            "Consulta el README del proyecto para configurarla en 2 minutos."
        )
    else:
        question = st.text_input(
            "Tu pregunta",
            placeholder="Ej: ¿Cuánto más gana un Senior que un Junior en este subconjunto?",
        )
        if st.button("Preguntar") and question:
            with st.spinner("Analizando los datos..."):
                try:
                    answer = ask_question(question, filtered_df, api_key)
                    # Escapamos los símbolos $ para que Streamlit no los
                    # interprete como fórmulas matemáticas (LaTeX).
                    safe_answer = answer.replace("$", r"\$")
                    st.success(safe_answer)
                    st.success(answer)
                except Exception as e:
                    st.error(f"No se pudo obtener respuesta: {e}")


if __name__ == "__main__":
    main()