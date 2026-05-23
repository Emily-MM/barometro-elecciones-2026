import os
import json
from datetime import datetime
from pytrends.request import TrendReq

CANDIDATES = {
    "keiko_fujimori": "Keiko Fujimori",
    "roberto_sanchez": "Roberto Sanchez"
}
def fetch_trends():
    pytrends = TrendReq(hl="es-PE", tz=-300)
    keywords = list(CANDIDATES.values())

    pytrends.build_payload(
        keywords,
        cat=0,
        timeframe="today 1-m",
        geo="PE"
    )

    data = pytrends.interest_over_time()
    related = pytrends.related_queries()

    result = {}
    for candidate_key, keyword in CANDIDATES.items():
        series = []
        dates = []
        current = 0

        if not data.empty and keyword in data.columns:
            series = data[keyword].tolist()
            dates = [str(d.date()) for d in data.index]
            current = int(series[-1]) if series else 0

        top_queries = []
        rising_queries = []
        if keyword in related:
            top_df = related[keyword].get("top")
            rising_df = related[keyword].get("rising")
            if top_df is not None and not top_df.empty:
                top_queries = top_df.head(5)["query"].tolist()
            if rising_df is not None and not rising_df.empty:
                rising_queries = rising_df.head(5)["query"].tolist()

        result[candidate_key] = {
            "keyword": keyword,
            "series": series,
            "dates": dates,
            "current": current,
            "top_queries": top_queries,
            "rising_queries": rising_queries
        }

        print(f"  {candidate_key}: índice actual = {current}")
        print(f"    Top búsquedas: {top_queries}")
        print(f"    En alza: {rising_queries}")

    return result

def main():
    today = datetime.now().strftime("%Y-%m-%d")
    print("Fetching Google Trends...")
    trends = fetch_trends()

    os.makedirs("data/raw", exist_ok=True)
    filepath = f"data/raw/trends_{today}.json"
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(trends, f, ensure_ascii=False, indent=2)

    print(f"\nGuardado en {filepath}")

if __name__ == "__main__":
    main()