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
TIKTOK_FILE   = DATA_DIR / f"tiktok_{TODAY}.json"
OUTPUT_FILE   = DATA_DIR / f"sentiment_{TODAY}.json"

MAX_TEXTS = 200
MAX_CHARS = 512

CANDIDATES = ["keiko_fujimori", "roberto_sanchez"]


def load_json(path: Path) -> dict:
    if not path.exists():
        print(f"[WARN] No se encontró {path}, se omite.")
        return {}
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def truncate(text: str) -> str:
    return text[:MAX_CHARS]


def get_texts_youtube(data: dict, candidate: str) -> list[str]:
    comments = data.get(candidate, {}).get("comments", [])
    return [truncate(c) for c in comments if isinstance(c, str) and c.strip()]


def get_texts_reddit(data: dict, candidate: str) -> list[str]:
    texts = data.get(candidate, {}).get("texts", [])
    return [truncate(t) for t in texts if isinstance(t, str) and t.strip()]


def get_texts_tiktok(data: dict, candidate: str) -> list[str]:
    texts = data.get(candidate, {}).get("texts", [])
    return [truncate(t) for t in texts if isinstance(t, str) and t.strip()]


def analyze_texts(analyzer, texts: list[str]) -> dict:
    if not texts:
        return {"positive": 0.0, "neutral": 0.0, "negative": 0.0, "count": 0}

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


def weighted_combined(sources: list[dict]) -> dict:
    total_n = sum(s["count"] for s in sources)
    if total_n == 0:
        return {"positive": 0.0, "neutral": 0.0, "negative": 0.0, "count": 0}
    return {
        "positive": round(sum(s["positive"] * s["count"] for s in sources) / total_n, 2),
        "neutral":  round(sum(s["neutral"]  * s["count"] for s in sources) / total_n, 2),
        "negative": round(sum(s["negative"] * s["count"] for s in sources) / total_n, 2),
        "count":    total_n,
    }


def main():
    print(f"[INFO] Fecha: {TODAY}")
    print("[INFO] Cargando modelo pysentimiento (robertuito)...")
    analyzer = create_analyzer(task="sentiment", lang="es")
    print("[INFO] Modelo cargado.")

    youtube_data = load_json(YOUTUBE_FILE)
    reddit_data  = load_json(REDDIT_FILE)
    tiktok_data  = load_json(TIKTOK_FILE)

    has_tiktok = bool(tiktok_data)
    print(f"[INFO] TikTok: {'encontrado' if has_tiktok else 'no disponible hoy'}")

    output = {"date": TODAY, "candidates": {}}

    for candidate in CANDIDATES:
        print(f"\n[INFO] Procesando: {candidate}")

        yt_texts     = get_texts_youtube(youtube_data, candidate)
        reddit_texts = get_texts_reddit(reddit_data, candidate)
        tiktok_texts = get_texts_tiktok(tiktok_data, candidate) if has_tiktok else []

        print(f"  YouTube : {len(yt_texts)} textos")
        print(f"  Reddit  : {len(reddit_texts)} textos")
        print(f"  TikTok  : {len(tiktok_texts)} textos")

        print("  Analizando YouTube...")
        yt_sent = analyze_texts(analyzer, yt_texts)

        print("  Analizando Reddit...")
        reddit_sent = analyze_texts(analyzer, reddit_texts)

        tiktok_sent = {"positive": 0.0, "neutral": 0.0, "negative": 0.0, "count": 0}
        if tiktok_texts:
            print("  Analizando TikTok...")
            tiktok_sent = analyze_texts(analyzer, tiktok_texts)

        sources = [yt_sent, reddit_sent]
        if tiktok_sent["count"] > 0:
            sources.append(tiktok_sent)

        combined = weighted_combined(sources)

        output["candidates"][candidate] = {
            "youtube":  yt_sent,
            "reddit":   reddit_sent,
            "tiktok":   tiktok_sent,
            "combined": combined,
        }

        print(f"  Combined → POS: {combined['positive']}% | NEU: {combined['neutral']}% | NEG: {combined['negative']}% ({combined['count']} textos)")

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n[OK] Guardado en {OUTPUT_FILE}")


if __name__ == "__main__":
    main()