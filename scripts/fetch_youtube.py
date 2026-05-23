import os
import json
from datetime import datetime
from dotenv import load_dotenv
from googleapiclient.discovery import build

load_dotenv()

API_KEY = os.getenv("YOUTUBE_API_KEY")
youtube = build("youtube", "v3", developerKey=API_KEY)

CANDIDATES = {
    "keiko_fujimori": ["Keiko Fujimori", "Keiko", "Fuerza Popular"],
    "roberto_sanchez": ["Roberto Sánchez", "Roberto Sanchez", "Juntos por el Perú"]
}

def search_videos(query, max_results=10):
    response = youtube.search().list(
        q=query,
        part="id,snippet",
        type="video",
        maxResults=max_results,
        relevanceLanguage="es",
        regionCode="PE",
        order="date"
    ).execute()
    return [item["id"]["videoId"] for item in response.get("items", [])]

def get_comments(video_id, max_results=100):
    comments = []
    try:
        response = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=max_results,
            textFormat="plainText"
        ).execute()
        for item in response.get("items", []):
            text = item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
            comments.append(text)
    except Exception:
        pass
    return comments

def fetch_candidate(candidate_key, search_terms):
    all_comments = []
    video_ids = []

    for term in search_terms:
        ids = search_videos(term, max_results=5)
        video_ids.extend(ids)

    video_ids = list(set(video_ids))
    print(f"  Videos encontrados para {candidate_key}: {len(video_ids)}")

    for video_id in video_ids:
        comments = get_comments(video_id)
        all_comments.extend(comments)

    print(f"  Comentarios recolectados: {len(all_comments)}")
    return all_comments

def main():
    today = datetime.now().strftime("%Y-%m-%d")
    output = {}

    for candidate_key, search_terms in CANDIDATES.items():
        print(f"\nFetching YouTube: {candidate_key}")
        comments = fetch_candidate(candidate_key, search_terms)
        output[candidate_key] = {
            "comments": comments,
            "count": len(comments)
        }

    os.makedirs("docs/data/raw", exist_ok=True)
    filepath = f"docs/data/raw/youtube_{today}.json"
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\nGuardado en {filepath}")

if __name__ == "__main__":
    main()