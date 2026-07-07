"""
eda.py
Análisis exploratorio de datos (EDA) sobre salarios tech.

Ejecutar con:  python src/eda.py
Genera gráficas en reports/figures/ y muestra un resumen en consola.
"""

import matplotlib.pyplot as plt
import seaborn as sns

from data_loader import load_salaries

sns.set_theme(style="whitegrid")
FIGURES_DIR = "reports/figures"


def print_summary(df):
    print("=" * 60)
    print("RESUMEN GENERAL")
    print("=" * 60)
    print(f"Total de registros analizados: {len(df):,}")
    print(f"Rango de años: {df['work_year'].min()} - {df['work_year'].max()}")
    print(f"Salario medio (USD): ${df['salary_in_usd'].mean():,.0f}")
    print(f"Salario mediano (USD): ${df['salary_in_usd'].median():,.0f}")
    print()
    print("Salario medio por nivel de experiencia:")
    print(
        df.groupby("experience_label")["salary_in_usd"]
        .mean()
        .sort_values(ascending=False)
        .round(0)
    )


def plot_salary_by_experience(df):
    """Boxplot de salario por nivel de experiencia."""
    order = ["Junior (Entry-level)", "Mid-level", "Senior", "Executive"]
    plt.figure(figsize=(9, 5))
    sns.boxplot(
        data=df,
        x="experience_label",
        y="salary_in_usd",
        order=order,
        hue="experience_label",
        legend=False,
        palette="viridis",
    )
    plt.title("Distribución de salarios por nivel de experiencia")
    plt.xlabel("Nivel de experiencia")
    plt.ylabel("Salario anual (USD)")
    plt.ticklabel_format(style="plain", axis="y")
    plt.tight_layout()
    plt.savefig(f"{FIGURES_DIR}/salary_by_experience.png", dpi=150)
    plt.close()


def plot_top_job_titles(df, top_n=10):
    """Top N puestos con salario medio más alto (con volumen mínimo de datos)."""
    counts = df["job_title"].value_counts()
    valid_titles = counts[counts >= 30].index  # evitamos puestos con 1-2 registros

    top = (
        df[df["job_title"].isin(valid_titles)]
        .groupby("job_title")["salary_in_usd"]
        .mean()
        .sort_values(ascending=False)
        .head(top_n)
    )

    plt.figure(figsize=(9, 6))
    sns.barplot(x=top.values, y=top.index, hue=top.index, legend=False, palette="mako")
    plt.title(f"Top {top_n} puestos mejor pagados (min. 30 registros)")
    plt.xlabel("Salario medio anual (USD)")
    plt.ylabel("")
    plt.tight_layout()
    plt.savefig(f"{FIGURES_DIR}/top_job_titles.png", dpi=150)
    plt.close()


def plot_remote_vs_salary(df):
    """Relación entre % de trabajo remoto y salario medio."""
    remote_labels = {0: "Presencial", 50: "Híbrido", 100: "Remoto total"}
    df = df.copy()
    df["remote_label"] = df["remote_ratio"].map(remote_labels)

    plt.figure(figsize=(7, 5))
    sns.barplot(
        data=df,
        x="remote_label",
        y="salary_in_usd",
        order=["Presencial", "Híbrido", "Remoto total"],
        hue="remote_label",
        legend=False,
        palette="crest",
    )
    plt.title("Salario medio según modalidad de trabajo")
    plt.xlabel("")
    plt.ylabel("Salario medio anual (USD)")
    plt.tight_layout()
    plt.savefig(f"{FIGURES_DIR}/remote_vs_salary.png", dpi=150)
    plt.close()


if __name__ == "__main__":
    data = load_salaries()
    print_summary(data)
    plot_salary_by_experience(data)
    plot_top_job_titles(data)
    plot_remote_vs_salary(data)
    print(f"\nGráficas guardadas en {FIGURES_DIR}/")