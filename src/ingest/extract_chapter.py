"""
Content-driven chapter extraction.
Finds the chapter start by title match, skips front-matter pages,
extracts to end of file.

Run: python -m src.ingest.extract_chapter --pdf data/raw_pdfs/jess301.pdf --chapter-no 1
Output: data/chapter1_raw.jsonl
"""
import argparse
import json
import re
from pathlib import Path

import pymupdf as fitz
import yaml 

CONFIG_PATH = Path("config/subjects.yaml")


MOJIBAKE_FIXES = {
    "\u00e2\u20ac\u2122": "'",
    "\u00e2\u20ac\u02dc": "'",
    "\u00e2\u20ac\u0153": '"',
    "\u00e2\u20ac\u009d": '"',
    "\u00e2\u20ac\u201c": "\u2014",
    "\u00e2\u20ac\u201d": "\u2014",
    "\u00e2\u20ac\u2013": "\u2013",
    "\u00e2\u20ac\u00a6": "\u2026",
    "\u00c2 ": " ",
}


def clean_text(t: str, chapter_title: str | None = None) -> str:
    for bad, good in MOJIBAKE_FIXES.items():
        t = t.replace(bad, good)
    t = re.sub(r"\u00a9 NCERT not to be republished", "", t, flags=re.IGNORECASE)
    t = re.sub(r"\bReprint\s+\d{4}-\d{2}\b", "", t)
    # Book running header + page number
    t = re.sub(r"^India and the Contemporary World\s+\d+\s*", "", t)   
    # Page number + Title-Case running header (structural, works for any chapter)
    t = re.sub(r"^\d{1,3}\s+(?:[A-Z][A-Za-z'\-]+\s+){1,6}", "", t)
    # Line-wrap hyphenation
    t = re.sub(r"(\w)- (\w)", r"\1-\2", t)
    t = re.sub(r"\s+", " ", t)
    return t.strip()


def normalize(s: str) -> str:
    """Lowercase, collapse whitespace, strip punctuation for fuzzy title match."""
    s = s.lower()
    s = re.sub(r"[^\w\s]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def find_chapter_start(doc: fitz.Document, chapter_title: str, max_scan: int = 10) -> int:
    """
    Return the 0-indexed page where the chapter title first appears.
    Scans only the first `max_scan` pages. Raises if not found.
    """
    target = normalize(chapter_title)
    for i in range(min(max_scan, len(doc))):
        page_text = normalize(doc[i].get_text())
        if target in page_text:
            return i
    raise ValueError(
        f"Chapter title '{chapter_title}' not found in first {max_scan} pages of PDF. "
        f"Check config/subjects.yaml and the PDF."
    )


def load_chapter_title(chapter_no: int) -> str:
    cfg = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))
    return cfg["class_10"]["social_science"]["streams"]["history"]["chapters"][chapter_no]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdf", required=True, help="Path to chapter PDF")
    ap.add_argument("--chapter-no", type=int, required=True, help="Chapter number from config")
    args = ap.parse_args()

    title = load_chapter_title(args.chapter_no)
    doc = fitz.open(args.pdf)
    start = find_chapter_start(doc, title)

    print(f"PDF: {args.pdf}")
    print(f"Total pages: {len(doc)}")
    print(f"Chapter title: {title}")
    print(f"Chapter start: PDF page {start + 1} (skipping {start} front-matter page(s))")

    pages = []
    for i in range(start, len(doc)):
        text = clean_text(doc[i].get_text(), chapter_title=title)
        pages.append({"pdf_page": i + 1, "text": text, "text_len": len(text)})

    out = Path(f"data/chapter{args.chapter_no}_raw.jsonl")
    with out.open("w", encoding="utf-8") as f:
        for p in pages:
            f.write(json.dumps(p, ensure_ascii=False) + "\n")

    total = sum(p["text_len"] for p in pages)
    empties = sum(1 for p in pages if p["text_len"] < 50)
    print(f"\nPages extracted: {len(pages)}")
    print(f"Total chars: {total:,}")
    print(f"Avg chars/page: {total / len(pages):.0f}")
    print(f"Empty/near-empty pages: {empties}")
    print(f"Output: {out}")


if __name__ == "__main__":
    main()