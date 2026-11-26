# Development Phases

| Phase | Goal | Gate |
|---|---|---|
| 0 | Contracts (schemas, config, prompts) | schemas validate, pytest green |
| 1 | Ingestion & chunking (one chapter first) | ≥90% coherent chunks on inspection |
| 2 | Embedding & retrieval | recall@5 ≥ 0.8 on hand-built eval |
| 3 | Generation (4 types: MCQ, 2m Short, Source-based, Chronology; Easy; History) | ≥80% PYQ format fidelity, 0 ungrounded |
| 4 | Expand types/difficulty/subjects | generalizes to 2nd subject |
| 5 | Paper assembly from blueprint | zero weightage violations |

## Phase 0 checklist
- [x] schemas/chunk.json, question.json, blueprint.json
- [x] config/subjects.yaml (verified against PDF)
- [x] eval/easy_definition.md (10 anchors written)
- [x] prompts/ (mcq + short2 stubs)
- [x] requirements.txt installs clean
- [x] pytest green
- [x] LICENSE, README, .gitignore, .env.example

## Phase 1 checklist
- [x] Content-driven chapter extractor (`src/ingest/extract_chapter.py`)
- [x] Chapter start auto-detected (Ch 1: skip 2, Ch 2: skip 0, Ch 3: skip 2)
- [x] Mojibake fixed via `\uXXXX` replacement map (verified via `repr()`)
- [x] All 3 chapters extract clean (0 empty pages, ~2200–2400 chars/page avg)
- [x] Chunker written (`src/ingest/chunk.py`) with marker-based content_type detection
- [x] Ch 1–3 chunked: 59 / 54 / 55 chunks (3 / 0 / 2 skipped)
- [x] All 3 chapters inspected: no mojibake, no page headers, no `Reprint` residue
- [x] Header pattern generalized structurally (Ch 3 bug fixed; works across all chapter titles)
- [x] Figure-dependent ratio: Ch 1 8.3%, Ch 2 1.9%, Ch 3 0.0%
- [x] Known imperfections accepted: Ch 3 map-label chunk (1/55), Ch 2 mid-sentence starts (2–3/54)
- [x] Phase 1 gate passed: ≥90% coherent on manual inspection of all 3 chapters

## Phase 2 checklist
- [x] `src/embed/embed_chunks.py` — 168 chunks embedded into Chroma
- [x] `eval/retrieval_eval.jsonl` — 28 queries (18 keyword + 10 paraphrase) with chapter labels
- [x] `src/retrieve/eval_retrieval.py` — reports global + scoped recall@5 and MRR
- [x] Scoped recall@5 = 1.000, MRR = 0.830
- [x] Global recall@5 = 1.000, MRR = 0.830
- [x] Miss analysis: all 8 non-rank-1 queries are paraphrase queries (expected)
- [x] Phase 2 gate passed

## Phase 3 checklist
- [ ] `src/generate/generate.py` written — retrieve → LLM → JSON
- [ ] `src/generate/verifier.py` written — LLM-as-judge grounding check
- [ ] MCQ generation working on Chapter 2
- [ ] Short-answer (2-mark) generation working on Chapter 2
- [ ] Grounding verifier rejects at least one ungrounded question (demonstrable)
- [ ] ≥80% format fidelity on PYQ benchmark (or waived for time)
- [ ] Phase 3 gate passed

## Windows gotchas
- `Out-File -Encoding utf8` on PS 5.x writes a BOM; write JSON/JSONL from Python
  with `encoding="utf-8"` instead.
- `Get-Content` on PS 5.x mis-displays UTF-8; trust Python's `print()` for text
  verification, or use `[Console]::OutputEncoding = [System.Text.Encoding]::UTF8`
  and `Get-Content -Encoding UTF8`.
- Never edit non-ASCII source files via PowerShell heredoc — the shell
  re-encodes smart quotes and dashes, causing double-mojibake. Use VS Code.
- `utf8NoBOM` encoding is PS 7+ only. On PS 5.x, use
  `[System.IO.File]::WriteAllText(path, content, [System.Text.UTF8Encoding]::new($false))`.