"""
Embed all chunks into Chroma.
Run: python -m src.embed.embed_chunks
"""
import os
import sqlite3
from pathlib import Path

import chromadb
import ollama
from dotenv import load_dotenv

load_dotenv()

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DB_PATH = REPO_ROOT / "data" / "chunks.db"
CHROMA_DIR = REPO_ROOT / "data" / "chroma"
EMBED_MODEL = os.getenv("EMBED_MODEL", "qwen3-embedding:0.6b")


def main():
    conn = sqlite3.connect(DB_PATH)
    rows = list(conn.execute(
        "SELECT chunk_id, chapter_no, chapter_title, content_type, "
        "is_figure_dependent, page_no, text FROM chunks"
    ))
    print(f"Embedding {len(rows)} chunks with {EMBED_MODEL}...")

    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    try:
        client.delete_collection("ncert_chunks")
    except Exception:
        pass
    col = client.create_collection("ncert_chunks", metadata={"hnsw:space": "cosine"})

    ids, embeddings, metadatas, documents = [], [], [], []
    for i, (cid, ch_no, ch_title, ctype, fig, page, text) in enumerate(rows):
        embed_text = f"{ch_title} > {text}"
        resp = ollama.embed(model=EMBED_MODEL, input=embed_text)
        ids.append(cid)
        embeddings.append(resp["embeddings"][0])
        metadatas.append({
            "chapter_no": ch_no,
            "chapter_title": ch_title,
            "content_type": ctype,
            "is_figure_dependent": bool(fig),
            "page_no": page,
        })
        documents.append(text)
        if (i + 1) % 20 == 0:
            print(f"  embedded {i + 1}/{len(rows)}")

    col.add(ids=ids, embeddings=embeddings, metadatas=metadatas, documents=documents)
    print(f"Done. Collection 'ncert_chunks' has {col.count()} items.")


if __name__ == "__main__":
    main()