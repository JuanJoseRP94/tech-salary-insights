"""
data_loader.py
Carga y limpieza del dataset de salarios tech.

Fuente: https://github.com/foorilla/ai-jobs-net-salaries (dominio público, CC0)
"""

import os
import urllib.request

import pandas as pd

DATASET_URL = "https://raw.githubusercontent.com/foorilla/ai-jobs-net-salaries/main/salaries.csv"

# Mapeos para convertir los códigos del dataset original en etiquetas legibles.

# Mapeos para convertir los códigos del dataset original en etiquetas legibles.
EXPERIENCE_LABELS = {
    "EN": "Junior (Entry-level)",
    "MI": "Mid-level",
    "SE": "Senior",
    "EX": "Executive",
}

COMPANY_SIZE_LABELS = {
    "S": "Pequeña (<50 empleados)",
    "M": "Mediana (50-250)",
    "L": "Grande (>250)",
}

EMPLOYMENT_TYPE_LABELS = {
    "FT": "Tiempo completo",
    "PT": "Tiempo parcial",
    "CT": "Contrato",
    "FL": "Freelance",
}


def load_salaries(path: str = "data/salaries.csv") -> pd.DataFrame:
    """
    Carga el dataset de salarios y añade columnas legibles.

    Args:
        path: ruta al CSV de salarios.

    Returns:
        DataFrame limpio y enriquecido con etiquetas legibles.
    """
    # Si el CSV no existe (p.ej. en Streamlit Cloud, donde no se sube a Git),
    # lo descargamos automáticamente desde la fuente pública antes de leerlo.
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        urllib.request.urlretrieve(DATASET_URL, path)

    df = pd.read_csv(path)

    # Copiamos en vez de mutar in-place, buena práctica para evitar
    # efectos secundarios inesperados si esta función se reutiliza.
    df = df.copy()

    df["experience_label"] = df["experience_level"].map(EXPERIENCE_LABELS)
    df["company_size_label"] = df["company_size"].map(COMPANY_SIZE_LABELS)
    df["employment_type_label"] = df["employment_type"].map(EMPLOYMENT_TYPE_LABELS)

    # Nos quedamos solo con años con volumen de datos suficiente para
    # que las comparaciones sean fiables (2020-2022 tienen muy pocas filas).
    df = df[df["work_year"] >= 2023].reset_index(drop=True)

    return df


if __name__ == "__main__":
    data = load_salaries()
    print(f"Filas tras limpieza: {len(data)}")
    print(data.head())