"""
analyze_sentiment.py
Barómetro Digital 2026

Lee los textos de youtube_YYYY-MM-DD.json y reddit_YYYY-MM-DD.json,
corre pysentimiento (robertuito) sobre cada texto y guarda los scores
en data/raw/sentiment_YYYY-MM-DD.json
"""

import json
import os
from datetime import date
from pathlib import Path

from pysentimiento import create_analyzer
from dotenv import load_dotenv

load_dotenv()

TODAY = date.today().isoformat()          
DATA_DIR = Path("docs/data/raw")

YOUTUBE_FILE  = DATA_DIR / f"youtube_{TODAY}.json"
REDDIT_FILE   = DATA_DIR / f"reddit_{TODAY}.json"
OUTPUT_FILE   = DATA_DIR / f"sentiment_{TODAY}.json"

MAX_TEXTS     = 200   
MAX_CHARS     = 512   

CANDIDATES    = ["keiko_fujimori", "roberto_sanchez"]

def load_json(path: Path) -> dict:
    if not path.exists():
        print(f"[WARN] No se encontró {path}, se omite.")
        return {}
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def truncate(text: str) -> str:
    """Trunca el texto al límite del modelo."""
    return text[:MAX_CHARS]


def get_texts_youtube(data: dict, candidate: str) -> list[str]:
    """Extrae comentarios de YouTube para un candidato."""
    candidate_data = data.get(candidate, {})
    comments = candidate_data.get("comments", [])
    return [truncate(c) for c in comments if isinstance(c, str) and c.strip()]


def get_texts_reddit(data: dict, candidate: str) -> list[str]:
    """Extrae textos de Reddit para un candidato."""
    candidate_data = data.get(candidate, {})
    texts = candidate_data.get("texts", [])
    return [truncate(t) for t in texts if isinstance(t, str) and t.strip()]


def analyze_texts(analyzer, texts: list[str]) -> dict:
    """
    Corre el modelo sobre una lista de textos (ya truncados).
    Devuelve scores promedio POS/NEU/NEG como porcentajes (0–100).
    """
    if not texts:
        return {"positive": 0.0, "neutral": 0.0, "negative": 0.0, "count": 0}

    # Limitar cantidad
    sample = texts[:MAX_TEXTS]

    pos_total = neu_total = neg_total = 0.0

    for text in sample:
        try:
            result = analyzer.predict(text)
            pos_total += result.probas.get("POS", 0.0)
            neu_total += result.probas.get("NEU", 0.0)
            neg_total += result.probas.get("NEG", 0.0)
        except Exception as e:
            print(f"[WARN] Error analizando texto: {e}")
            continue

    n = len(sample)
    return {
        "positive": round((pos_total / n) * 100, 2),
        "neutral":  round((neu_total / n) * 100, 2),
        "negative": round((neg_total / n) * 100, 2),
        "count":    n,
    }

def main():
    print(f"[INFO] Fecha: {TODAY}")
    print("[INFO] Cargando modelo pysentimiento (robertuito)...")
    analyzer = create_analyzer(task="sentiment", lang="es")
    print("[INFO] Modelo cargado.")

    youtube_data = load_json(YOUTUBE_FILE)
    reddit_data  = load_json(REDDIT_FILE)

    output = {"date": TODAY, "candidates": {}}

    for candidate in CANDIDATES:
        print(f"\n[INFO] Procesando: {candidate}")

        yt_texts     = get_texts_youtube(youtube_data, candidate)
        reddit_texts = get_texts_reddit(reddit_data, candidate)

        print(f"  YouTube : {len(yt_texts)} textos")
        print(f"  Reddit  : {len(reddit_texts)} textos")

        print("  Analizando YouTube...")
        yt_sentiment = analyze_texts(analyzer, yt_texts)

        print("  Analizando Reddit...")
        reddit_sentiment = analyze_texts(analyzer, reddit_texts)

        yt_n     = yt_sentiment["count"]
        reddit_n = reddit_sentiment["count"]
        total_n  = yt_n + reddit_n

        if total_n > 0:
            combined = {
                "positive": round((yt_sentiment["positive"] * yt_n + reddit_sentiment["positive"] * reddit_n) / total_n, 2),
                "neutral":  round((yt_sentiment["neutral"]  * yt_n + reddit_sentiment["neutral"]  * reddit_n) / total_n, 2),
                "negative": round((yt_sentiment["negative"] * yt_n + reddit_sentiment["negative"] * reddit_n) / total_n, 2),
                "count":    total_n,
            }
        else:
            combined = {"positive": 0.0, "neutral": 0.0, "negative": 0.0, "count": 0}

        output["candidates"][candidate] = {
            "youtube":  yt_sentiment,
            "reddit":   reddit_sentiment,
            "combined": combined,
        }

        print(f"  Combined → POS: {combined['positive']}% | NEU: {combined['neutral']}% | NEG: {combined['negative']}% ({combined['count']} textos)")

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n[OK] Guardado en {OUTPUT_FILE}")


if __name__ == "__main__":
    main()