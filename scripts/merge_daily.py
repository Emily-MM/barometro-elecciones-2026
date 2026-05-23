import json
from datetime import date
from pathlib import Path

TODAY   = date.today().isoformat()
RAW_DIR = Path("docs/data/raw")
OUT_DIR = Path("docs/data")

YOUTUBE_FILE   = RAW_DIR / f"youtube_{TODAY}.json"
REDDIT_FILE    = RAW_DIR / f"reddit_{TODAY}.json"
TRENDS_FILE    = RAW_DIR / f"trends_{TODAY}.json"
TIKTOK_FILE    = RAW_DIR / f"tiktok_{TODAY}.json"
SENTIMENT_FILE = RAW_DIR / f"sentiment_{TODAY}.json"
OUTPUT_FILE    = OUT_DIR / f"{TODAY}.json"

CANDIDATES = ["keiko_fujimori", "roberto_sanchez"]


def load_json(path: Path) -> dict:
    if not path.exists():
        print(f"[WARN] No se encontró {path}, se omite.")
        return {}
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def empty_candidate() -> dict:
    return {
        "mentions": {
            "youtube": 0,
            "reddit":  0,
            "tiktok":  0,
            "total":   0,
        },
        "sentiment": {
            "positive": 0.0,
            "neutral":  0.0,
            "negative": 0.0,
            "count":    0,
        },
        "sentiment_by_source": {
            "youtube": {"positive": 0.0, "neutral": 0.0, "negative": 0.0, "count": 0},
            "reddit":  {"positive": 0.0, "neutral": 0.0, "negative": 0.0, "count": 0},
            "tiktok":  {"positive": 0.0, "neutral": 0.0, "negative": 0.0, "count": 0},
        },
        "trends_index":   0,
        "trends_series":  [],
        "trends_dates":   [],
        "top_queries":    [],
        "rising_queries": [],
    }


def merge(youtube: dict, reddit: dict, trends: dict, tiktok: dict, sentiment: dict) -> dict:
    output = {"date": TODAY, "candidates": {}}

    for candidate in CANDIDATES:
        data = empty_candidate()

        yt = youtube.get(candidate, {})
        yt_count = yt.get("count", 0)
        data["mentions"]["youtube"] = yt_count

        rd = reddit.get(candidate, {})
        rd_count = rd.get("text_count", rd.get("count", 0))
        data["mentions"]["reddit"] = rd_count

        tk = tiktok.get(candidate, {})
        tk_count = tk.get("text_count", tk.get("count", 0))
        data["mentions"]["tiktok"] = tk_count

        data["mentions"]["total"] = yt_count + rd_count + tk_count

        sent = sentiment.get("candidates", {}).get(candidate, {})
        if sent:
            combined = sent.get("combined", {})
            data["sentiment"] = {
                "positive": combined.get("positive", 0.0),
                "neutral":  combined.get("neutral",  0.0),
                "negative": combined.get("negative", 0.0),
                "count":    combined.get("count",    0),
            }
            data["sentiment_by_source"]["youtube"] = sent.get("youtube", data["sentiment_by_source"]["youtube"])
            data["sentiment_by_source"]["reddit"]  = sent.get("reddit",  data["sentiment_by_source"]["reddit"])
            data["sentiment_by_source"]["tiktok"]  = sent.get("tiktok",  data["sentiment_by_source"]["tiktok"])

        tr = trends.get(candidate, {})
        if tr:
            data["trends_index"]   = tr.get("current", 0)
            data["trends_series"]  = tr.get("series", [])
            data["trends_dates"]   = tr.get("dates", [])
            data["top_queries"]    = tr.get("top_queries", [])
            data["rising_queries"] = tr.get("rising_queries", [])

        output["candidates"][candidate] = data

        tk_str = f" | tiktok={tk_count}" if tk_count else ""
        print(f"[OK] {candidate}: menciones={data['mentions']['total']}{tk_str} | trends={data['trends_index']} | sentiment_count={data['sentiment']['count']}")

    return output


def main():
    print(f"[INFO] Mergeando datos del {TODAY}...")

    youtube   = load_json(YOUTUBE_FILE)
    reddit    = load_json(REDDIT_FILE)
    trends    = load_json(TRENDS_FILE)
    tiktok    = load_json(TIKTOK_FILE)
    sentiment = load_json(SENTIMENT_FILE)

    result = merge(youtube, reddit, trends, tiktok, sentiment)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"\n[OK] Guardado en {OUTPUT_FILE}")


if __name__ == "__main__":
    main()