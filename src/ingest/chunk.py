"""
Turn extracted pages into metadata-tagged chunks.
Run: python -m src.ingest.chunk --chapter-no 1
Output: data/chunks.db (SQLite)
"""
import argparse
import json
import re
import sqlite3
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
CONFIG_PATH = REPO_ROOT / "config" / "subjects.yaml"
DB_PATH = REPO_ROOT / "data" / "chunks.db"

MARKERS = [
    (r"\bNew words\b", "glossary"),
    (r"\bActivity\b", "box"),
    (r"\bSource\s*\d*\b", "source_extract"),
    (r"(Exercises|Let.s Recall|Let.s Discuss|Let.s Discuss more|Let.s Do)", "exercise"),
    (r"\bTimeline\b", "timeline"),
]

FIGURE_PATTERNS = [
    r"\bFig\.?\s*\d+",
    r"see (the )?figure",
    r"refer to (the )?(map|figure|image|picture)",
    r"look at (the )?(figure|image|map|picture)",
    r"as shown in",
    r"this print",
    r"this image",
    r"the picture",
]


def clean(t: str, chapter_title: str | None = None) -> str:
    t = re.sub(r"\bReprint\s+\d{4}-\d{2}\b", "", t)
    t = re.sub(r"^India and the Contemporary World\s+\d+\s*", "", t)
    t = re.sub(r"^\d{1,3}\s+(?:[A-Z][A-Za-z'\-]+\s+){1,6}", "", t)
    return re.sub(r"\s+", " ", t).strip()


def load_chapter_meta(chapter_no: int) -> dict:
    cfg = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))
    hist = cfg["class_10"]["social_science"]["streams"]["history"]
    return {
        "chapter_no": chapter_no,
        "chapter_title": hist["chapters"][chapter_no],
        "book_title": cfg["class_10"]["social_science"]["book"],
    }


def detect_type(text: str) -> str:
    for pattern, ctype in MARKERS:
        if re.search(pattern, text[:200], re.IGNORECASE):
            return ctype
    return "prose"


def is_figure_dependent(text: str) -> bool:
    strong_patterns = [
        r"^Fig\.?\s*\d+",
        r"^Activity\s+Fig\.?\s*\d+",
        r"^Box\s+Fig\.?\s*\d+",
        r"^(This (print|image|picture|map))",
        r"^(Look at|Study|Observe) (the )?(image|figure|map|picture)",
        r"describe the (image|figure|picture|map)",
        r"in what way does this",
    ]
    return any(re.search(p, text, re.IGNORECASE) for p in strong_patterns)


def is_label_dump(text: str) -> bool:
    words = text.split()[:60]
    if len(words) < 10:
        return False
    upper_ratio = sum(1 for w in words if w.isupper() and len(w) > 1) / len(words)
    return upper_ratio > 0.4


QUESTION_VERBS = r"^(Discuss|Describe|Imagine|Explain|Analyse|Analyze|Write|Comment|List|State|Identify)\b"


def is_question_fragment(text: str) -> bool:
    """Detect short activity-question fragments (not content)."""
    return len(text) < 200 and bool(re.match(QUESTION_VERBS, text, re.IGNORECASE))


def trim_glossary(seg: str, max_len: int = 500) -> str:
    # Try to cut at the first period after the definition
    m = re.match(r"(New words\s+\w+\s*[–-]\s*[^.]{5,300}\.)", seg)
    if m:
        return m.group(1).strip()
    # Fallback: hard cap at max_len
    return seg[:max_len].rsplit(".", 1)[0] + "." if "." in seg[:max_len] else seg[:max_len]


def split_into_chunks(page_text: str, chapter_title: str, max_chars: int = 1500) -> list[str]:
    positions = [0]
    for pattern, _ in MARKERS:
        for m in re.finditer(pattern, page_text, re.IGNORECASE):
            positions.append(m.start())
    positions = sorted(set(positions + [len(page_text)]))

    segments = []
    for i in range(len(positions) - 1):
        seg = clean(page_text[positions[i]:positions[i + 1]], chapter_title=chapter_title)
        if len(seg) > 20:
            segments.append(seg)

    chunks = []
    for seg in segments:
        if len(seg) <= max_chars:
            chunks.append(seg)
        else:
            sentences = re.split(r"(?<=[.!?])\s+", seg)
            buf = ""
            for s in sentences:
                if len(buf) + len(s) > max_chars and buf:
                    chunks.append(buf.strip())
                    buf = s
                else:
                    buf += (" " if buf else "") + s
            if buf.strip():
                chunks.append(buf.strip())
    return chunks


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--chapter-no", type=int, required=True)
    args = ap.parse_args()

    meta = load_chapter_meta(args.chapter_no)
    pages_path = REPO_ROOT / "data" / f"chapter{args.chapter_no}_raw.jsonl"
    pages = [json.loads(l) for l in pages_path.read_text(encoding="utf-8").splitlines() if l.strip()]

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS chunks (
            chunk_id TEXT PRIMARY KEY,
            class INTEGER, subject TEXT, stream TEXT, book_title TEXT,
            chapter_no INTEGER, chapter_title TEXT,
            section_title TEXT, subsection_title TEXT,
            content_type TEXT, is_figure_dependent INTEGER,
            page_no INTEGER, text TEXT
        )
    """)
    conn.execute("DELETE FROM chunks WHERE chapter_no = ?", (args.chapter_no,))

    total = 0
    skipped = 0
    for page in pages:
        page_no = page["pdf_page"]
        for idx, seg in enumerate(split_into_chunks(page["text"], meta["chapter_title"]), start=1):
            ctype = detect_type(seg)

            # Skip low-value chunks
            if len(seg) < 80:
                skipped += 1
                continue
            if is_label_dump(seg):
                skipped += 1
                continue
            if is_question_fragment(seg):
                skipped += 1
                continue

            # Trim contaminated glossaries
            if ctype == "glossary":
                seg = trim_glossary(seg)

            chunk_id = f"ss10_hist_ch{args.chapter_no:02d}_p{page_no:03d}_s{idx:02d}"
            conn.execute(
                "INSERT INTO chunks VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (
                    chunk_id, 10, "social_science", "history", meta["book_title"],
                    args.chapter_no, meta["chapter_title"],
                    "UNKNOWN", None,
                    ctype, int(is_figure_dependent(seg)),
                    page_no, seg,
                ),
            )
            total += 1
    conn.commit()
    conn.close()

    print(f"Chapter {args.chapter_no}: {total} chunks ({skipped} skipped) → {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    for ctype, n in conn.execute(
        "SELECT content_type, COUNT(*) FROM chunks WHERE chapter_no=? GROUP BY content_type ORDER BY COUNT(*) DESC",
        (args.chapter_no,),
    ):
        print(f"  {ctype:15s} {n}")
    conn.close()


if __name__ == "__main__":
    main()