"""
process_zeeschuimer.py
Barómetro Digital 2026

Procesa exports NDJSON de Zeeschuimer (TikTok) y los convierte
al schema del proyecto.

Estructura esperada en zeeschuimer/:
  zeeschuimer/
  ├── keiko_comments.ndjson
  ├── keiko_videos.ndjson
  ├── sanchez_comments.ndjson
  └── sanchez_videos.ndjson

Output:
  docs/data/raw/tiktok_YYYY-MM-DD.json

Uso:
  python scripts/process_zeeschuimer.py
  python scripts/process_zeeschuimer.py --date 2026-05-31  (fecha manual)
"""

import json
import sys
from datetime import date
from pathlib import Path

# ── Configuración ─────────────────────────────────────────────────────────────

# Fecha — por defecto hoy, o pasar --date YYYY-MM-DD como argumento
if "--date" in sys.argv:
    TODAY = sys.argv[sys.argv.index("--date") + 1]
else:
    TODAY = date.today().isoformat()

ZEESCHUIMER_DIR = Path("zeeschuimer")
OUT_DIR         = Path("docs/data/raw")
OUT_FILE        = OUT_DIR / f"tiktok_{TODAY}.json"

# Archivos esperados por candidato
FILES = {
    "keiko_fujimori": {
        "comments": ZEESCHUIMER_DIR / "keiko_comments.ndjson",
        "videos":   ZEESCHUIMER_DIR / "keiko_videos.ndjson",
    },
    "roberto_sanchez": {
        "comments": ZEESCHUIMER_DIR / "sanchez_comments.ndjson",
        "videos":   ZEESCHUIMER_DIR / "sanchez_videos.ndjson",
    },
}

# ── Helpers ───────────────────────────────────────────────────────────────────

def load_ndjson(path: Path) -> list[dict]:
    if not path.exists():
        print(f"  [WARN] No se encontró {path}, se omite.")
        return []
    items = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                items.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return items


def extract_comments(items: list[dict]) -> list[str]:
    """Extrae texto de comentarios (source_platform: tiktok-comments)."""
    texts = []
    for item in items:
        text = item.get("data", {}).get("text", "")
        if text and isinstance(text, str) and text.strip():
            # Filtrar URLs y textos muy cortos
            if not text.startswith("http") and len(text.strip()) > 3:
                texts.append(text.strip())
    return texts


def extract_descriptions(items: list[dict]) -> list[str]:
    """Extrae descripciones de videos."""
    texts = []
    for item in items:
        desc = item.get("data", {}).get("desc", "")
        if desc and isinstance(desc, str) and desc.strip():
            # Limpiar hashtags del inicio/final pero mantener el texto
            clean = desc.strip()
            if len(clean) > 5:
                texts.append(clean)
    return texts


def extract_video_meta(items: list[dict]) -> list[dict]:
    """Extrae metadata de videos para referencia."""
    videos = []
    for item in items:
        data = item.get("data", {})
        video_id = data.get("id", "")
        author = data.get("author", {})
        if isinstance(author, dict):
            author_id = author.get("uniqueId", "")
        else:
            author_id = ""
        
        if video_id:
            videos.append({
                "id": video_id,
                "url": f"https://www.tiktok.com/@{author_id}/video/{video_id}" if author_id else "",
                "description": data.get("desc", ""),
                "likes": data.get("stats", {}).get("diggCount", 0),
                "comments_count": data.get("stats", {}).get("commentCount", 0),
                "shares": data.get("stats", {}).get("shareCount", 0),
            })
    return videos


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print(f"[INFO] Procesando exports de Zeeschuimer para {TODAY}")
    output = {}

    for candidate, paths in FILES.items():
        print(f"\n[INFO] {candidate}")

        comment_items = load_ndjson(paths["comments"])
        video_items   = load_ndjson(paths["videos"])

        comments     = extract_comments(comment_items)
        descriptions = extract_descriptions(video_items)
        videos_meta  = extract_video_meta(video_items)

        # Combinar comentarios + descripciones como textos para sentimiento
        all_texts = comments + descriptions

        print(f"  Comentarios : {len(comments)}")
        print(f"  Descripciones: {len(descriptions)}")
        print(f"  Total textos : {len(all_texts)}")

        output[candidate] = {
            "texts":        all_texts,
            "comments":     comments,
            "descriptions": descriptions,
            "videos":       videos_meta,
            "text_count":   len(all_texts),
            "comment_count": len(comments),
            "video_count":  len(videos_meta),
            "source":       "zeeschuimer",
            "date":         TODAY,
        }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n[OK] Guardado en {OUT_FILE}")


if __name__ == "__main__":
    main()