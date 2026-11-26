"""
Evaluate retrieval on eval/retrieval_eval.jsonl.
Reports global recall@5 (no filter) and scoped recall@5 (chapter-filtered,
matching the teacher workflow).
Run: python -m src.retrieve.eval_retrieval
"""
import json
import os
from pathlib import Path

import chromadb
import ollama
from dotenv import load_dotenv

load_dotenv()

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
EVAL_PATH = REPO_ROOT / "eval" / "retrieval_eval.jsonl"
CHROMA_DIR = REPO_ROOT / "data" / "chroma"
EMBED_MODEL = os.getenv("EMBED_MODEL", "qwen3-embedding:0.6b")


def evaluate(col, cases, use_filter: bool) -> tuple[float, float, list]:
    """Return (recall@5, mrr, misses) for the given cases."""
    hits, mrr_total, misses = 0, 0.0, []
    for case in cases:
        q = case["query"]
        expected = set(case["expected_chunk_ids"])
        kwargs = {"query_embeddings": [ollama.embed(model=EMBED_MODEL, input=q)["embeddings"][0]], "n_results": 5}
        if use_filter:
            kwargs["where"] = {"chapter_no": case["chapter"]}
        retrieved = col.query(**kwargs)["ids"][0]

        hit = False
        for rank, rid in enumerate(retrieved, start=1):
            if rid in expected:
                hits += 1
                mrr_total += 1.0 / rank
                hit = True
                break
        if not hit:
            misses.append((q, case.get("chapter"), retrieved, expected))
    return hits / len(cases), mrr_total / len(cases), misses


def main():
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    col = client.get_collection("ncert_chunks")

    cases = [json.loads(l) for l in EVAL_PATH.read_text(encoding="utf-8").splitlines() if l.strip()]
    print(f"Eval set: {len(cases)} queries")

    for label, use_filter in [("Global (no filter)", False), ("Scoped (chapter-filtered)", True)]:
        recall, mrr, misses = evaluate(col, cases, use_filter)
        print(f"\n{label}:")
        print(f"  Recall@5: {recall:.3f}")
        print(f"  MRR:      {mrr:.3f}")
        if misses:
            print(f"  Misses ({len(misses)}):")
            for q, ch, ret, exp in misses[:5]:
                print(f"    Q: {q}  (ch{ch})")
                print(f"       expected: {list(exp)}")
                print(f"       got:      {ret}")


if __name__ == "__main__":
    main()