"""
visualizations.py
Gráficas interactivas (Plotly) para el dashboard de Streamlit.

Cada función recibe un DataFrame ya filtrado y devuelve una figura de Plotly,
lista para pasarse a st.plotly_chart().
"""

import plotly.express as px

EXPERIENCE_ORDER = ["Junior (Entry-level)", "Mid-level", "Senior", "Executive"]
COLOR_SEQUENCE = px.colors.sequential.Viridis


def fig_salary_by_experience(df):
    fig = px.box(
        df,
        x="experience_label",
        y="salary_in_usd",
        category_orders={"experience_label": EXPERIENCE_ORDER},
        color="experience_label",
        color_discrete_sequence=COLOR_SEQUENCE,
        labels={
            "experience_label": "Nivel de experiencia",
            "salary_in_usd": "Salario anual (USD)",
        },
        title="Distribución de salarios por nivel de experiencia",
    )
    fig.update_layout(showlegend=False)
    return fig


def fig_top_job_titles(df, top_n=10, min_count=15):
    counts = df["job_title"].value_counts()
    valid_titles = counts[counts >= min_count].index

    top = (
        df[df["job_title"].isin(valid_titles)]
        .groupby("job_title")["salary_in_usd"]
        .mean()
        .sort_values(ascending=False)
        .head(top_n)
        .reset_index()
    )

    fig = px.bar(
        top,
        x="salary_in_usd",
        y="job_title",
        orientation="h",
        color="salary_in_usd",
        color_continuous_scale="Viridis",
        labels={"salary_in_usd": "Salario medio anual (USD)", "job_title": ""},
        title=f"Top {top_n} puestos mejor pagados (mín. {min_count} registros)",
    )
    fig.update_layout(yaxis={"categoryorder": "total ascending"}, coloraxis_showscale=False)
    return fig


def fig_remote_vs_salary(df):
    remote_labels = {0: "Presencial", 50: "Híbrido", 100: "Remoto total"}
    data = df.copy()
    data["remote_label"] = data["remote_ratio"].map(remote_labels)

    fig = px.bar(
        data.groupby("remote_label", as_index=False)["salary_in_usd"].mean(),
        x="remote_label",
        y="salary_in_usd",
        category_orders={"remote_label": ["Presencial", "Híbrido", "Remoto total"]},
        color="remote_label",
        color_discrete_sequence=COLOR_SEQUENCE,
        labels={"remote_label": "", "salary_in_usd": "Salario medio anual (USD)"},
        title="Salario medio según modalidad de trabajo",
    )
    fig.update_layout(showlegend=False)
    return fig


def fig_salary_trend(df):
    trend = df.groupby("work_year", as_index=False)["salary_in_usd"].median()
    fig = px.line(
        trend,
        x="work_year",
        y="salary_in_usd",
        markers=True,
        labels={"work_year": "Año", "salary_in_usd": "Salario mediano anual (USD)"},
        title="Evolución del salario mediano por año",
    )
    fig.update_xaxes(dtick=1)
    return fig


def fig_company_size_comparison(df):
    fig = px.box(
        df,
        x="company_size_label",
        y="salary_in_usd",
        color="company_size_label",
        category_orders={
            "company_size_label": [
                "Pequeña (<50 empleados)",
                "Mediana (50-250)",
                "Grande (>250)",
            ]
        },
        color_discrete_sequence=COLOR_SEQUENCE,
        labels={"company_size_label": "Tamaño de empresa", "salary_in_usd": "Salario anual (USD)"},
        title="Distribución de salarios según tamaño de empresa",
    )
    fig.update_layout(showlegend=False)
    return fig