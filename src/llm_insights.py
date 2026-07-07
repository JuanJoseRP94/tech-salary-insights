"""
llm_insights.py
Integración con IA generativa (Groq, modelos open-source, capa gratuita)
para responder preguntas en lenguaje natural sobre el dataset filtrado.

Diseño clave: en vez de enviar las 150.000 filas al modelo (caro, lento,
e innecesario), calculamos un RESUMEN ESTADÍSTICO del subconjunto filtrado
y se lo damos como contexto. El modelo razona sobre esos números reales,
no sobre datos inventados.
"""

from groq import Groq

MODEL = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = """Eres un analista de datos experto en el mercado laboral tech.
Se te proporciona un RESUMEN ESTADÍSTICO real (no inventado) de una consulta
sobre salarios en tecnología, generado a partir de un dataset filtrado por
el usuario. Responde a la pregunta del usuario basándote EXCLUSIVAMENTE en
esos datos. Si la pregunta no se puede responder con el resumen disponible,
dilo explícitamente en vez de inventar cifras. Sé conciso (máximo 4-5 frases)
y cita los números concretos del resumen cuando sea relevante.
IMPORTANTE: nunca uses el símbolo $ para expresar cantidades, escribe
"USD" después del número (ej: "99297 USD" en vez de "$99,297")."""


def build_data_summary(df) -> str:
    """
    Construye un resumen estadístico compacto del DataFrame filtrado,
    en texto plano, listo para insertar en el prompt.
    """
    if df.empty:
        return "No hay datos disponibles para los filtros actuales."

    lines = []
    lines.append(f"Total de registros: {len(df):,}")
    lines.append(f"Años cubiertos: {df['work_year'].min()}-{df['work_year'].max()}")
    lines.append(f"Salario medio: ${df['salary_in_usd'].mean():,.0f}")
    lines.append(f"Salario mediano: ${df['salary_in_usd'].median():,.0f}")
    lines.append(f"Salario mínimo/máximo: ${df['salary_in_usd'].min():,.0f} / ${df['salary_in_usd'].max():,.0f}")

    lines.append("\nSalario medio por nivel de experiencia:")
    for level, salary in df.groupby("experience_label")["salary_in_usd"].mean().sort_values(ascending=False).items():
        lines.append(f"  - {level}: ${salary:,.0f}")

    lines.append("\nSalario medio por tamaño de empresa:")
    for size, salary in df.groupby("company_size_label")["salary_in_usd"].mean().sort_values(ascending=False).items():
        lines.append(f"  - {size}: ${salary:,.0f}")

    lines.append("\nTop 5 puestos más frecuentes y su salario medio:")
    top_titles = df["job_title"].value_counts().head(5)
    for title, count in top_titles.items():
        avg_salary = df[df["job_title"] == title]["salary_in_usd"].mean()
        lines.append(f"  - {title} ({count} registros): ${avg_salary:,.0f} de media")

    remote_pct = (df["remote_ratio"] == 100).mean() * 100
    lines.append(f"\nPorcentaje de puestos 100% remotos: {remote_pct:.0f}%")

    return "\n".join(lines)


def ask_question(question: str, df, api_key: str) -> str:
    """
    Envía la pregunta del usuario + el resumen de datos al modelo de Groq
    y devuelve la respuesta en texto.

    Lanza una excepción si la API falla (clave inválida, sin conexión, etc.);
    el llamador (app.py) es responsable de capturarla y mostrar un mensaje
    amigable al usuario.
    """
    summary = build_data_summary(df)
    client = Groq(api_key=api_key)

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"RESUMEN DE DATOS:\n{summary}\n\nPREGUNTA: {question}",
            },
        ],
        temperature=0.3,
        max_tokens=400,
    )
    return response.choices[0].message.content