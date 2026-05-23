import os
import json
import time
import requests
from datetime import datetime

HEADERS = {"User-Agent": "barometro-2026/1.0"}

SUBREDDITS = ["peru", "ATMP"]

CANDIDATES = {
    "keiko_fujimori": ["Keiko Fujimori", "Keiko", "Fuerza Popular"],
    "roberto_sanchez": ["Roberto Sánchez", "Roberto Sanchez", "Juntos por el Peru"]
}

def get_post_comments(subreddit, post_id, limit=50):
    url = f"https://www.reddit.com/r/{subreddit}/comments/{post_id}.json"
    try:
        response = requests.get(url, headers=HEADERS, params={"limit": limit}, timeout=10)
        response.raise_for_status()
        data = response.json()
        comments = []
        for item in data[1]["data"]["children"]:
            if item["kind"] == "t1":
                body = item["data"].get("body", "")
                if body and body != "[deleted]" and body != "[removed]":
                    comments.append(body)
        return comments
    except Exception as e:
        print(f"    Error obteniendo comentarios de {post_id}: {e}")
        return []

def search_subreddit(subreddit, query, limit=10):
    url = f"https://www.reddit.com/r/{subreddit}/search.json"
    params = {"q": query, "restrict_sr": True, "sort": "new", "limit": limit}
    try:
        response = requests.get(url, headers=HEADERS, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        posts = data["data"]["children"]
        results = []
        for post in posts:
            p = post["data"]
            results.append({
                "id": p.get("id", ""),
                "title": p.get("title", ""),
                "text": p.get("selftext", ""),
                "score": p.get("score", 0),
                "num_comments": p.get("num_comments", 0),
                "subreddit": subreddit
            })
        return results
    except Exception as e:
        print(f"  Error en r/{subreddit} query '{query}': {e}")
        return []

def fetch_candidate(candidate_key, search_terms):
    all_posts = []
    all_texts = []

    for subreddit in SUBREDDITS:
        for term in search_terms:
            posts = search_subreddit(subreddit, term)
            all_posts.extend(posts)
            time.sleep(1)

    seen = set()
    unique_posts = []
    for post in all_posts:
        if post["id"] not in seen:
            seen.add(post["id"])
            unique_posts.append(post)

    print(f"  Posts encontrados: {len(unique_posts)}")

    for post in unique_posts:
        all_texts.append(post["title"] + " " + post["text"])
        if post["num_comments"] > 0:
            comments = get_post_comments(post["subreddit"], post["id"])
            all_texts.extend(comments)
            print(f"    [{post['subreddit']}] '{post['title'][:50]}' → {len(comments)} comentarios")
            time.sleep(1)

    print(f"  Textos totales (posts + comentarios): {len(all_texts)}")
    return unique_posts, all_texts

def main():
    today = datetime.now().strftime("%Y-%m-%d")
    output = {}

    for candidate_key, search_terms in CANDIDATES.items():
        print(f"\nFetching Reddit: {candidate_key}")
        posts, texts = fetch_candidate(candidate_key, search_terms)
        output[candidate_key] = {
            "posts": posts,
            "texts": texts,
            "count": len(posts),
            "text_count": len(texts)
        }

    os.makedirs("docs/data/raw", exist_ok=True)
    filepath = f"docs/data/raw/reddit_{today}.json"
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\nGuardado en {filepath}")

if __name__ == "__main__":
    main()