"""Descarga el dataset de salarios tech desde la fuente pública."""
import urllib.request

URL = "https://raw.githubusercontent.com/foorilla/ai-jobs-net-salaries/main/salaries.csv"
DEST = "data/salaries.csv"

urllib.request.urlretrieve(URL, DEST)
print(f"Descargado en {DEST}")