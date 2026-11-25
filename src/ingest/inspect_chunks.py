"""Inspect chunks in data/chunks.db. Run: python -m src.ingest.inspect_chunks --chapter-no 1"""
import argparse
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "chunks.db"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--chapter-no", type=int, default=1)
    args = ap.parse_args()

    conn = sqlite3.connect(DB_PATH)
    ch = args.chapter_no

    print("=" * 70)
    print(f"NON-PROSE SAMPLES (chapter {ch})")
    print("=" * 70)
    for ctype, text in conn.execute(
        "SELECT content_type, text FROM chunks "
        "WHERE chapter_no=? AND content_type != 'prose' LIMIT 10",
        (ch,),
    ):
        print(f"[{ctype}] {text[:200]}")
        print()

    print("=" * 70)
    print("FIGURE-DEPENDENT RATIO")
    print("=" * 70)
    n = conn.execute(
        "SELECT COUNT(*) FROM chunks WHERE chapter_no=? AND is_figure_dependent=1",
        (ch,),
    ).fetchone()[0]
    t = conn.execute(
        "SELECT COUNT(*) FROM chunks WHERE chapter_no=?", (ch,)
    ).fetchone()[0]
    print(f"{n}/{t} ({100 * n / t:.1f}%)")

    print()
    print("=" * 70)
    print("RANDOM 10 CHUNKS (coherence check)")
    print("=" * 70)
    for (text,) in conn.execute(
        "SELECT text FROM chunks WHERE chapter_no=? ORDER BY RANDOM() LIMIT 10",
        (ch,),
    ):
        print(f"[{len(text)} chars] {text[:200]}")
        print()

    conn.close()


if __name__ == "__main__":
    main()