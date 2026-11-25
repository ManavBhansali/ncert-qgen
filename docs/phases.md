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
- [ ] Chunker written (`src/ingest/chunk.py`)
- [ ] Chapter 1 chunked into `data/chunks.db`
- [ ] Manual inspection passed (≥90% coherent, ≥85% correctly typed)
- [ ] Figure-dependency flag sanity check (10–20% expected)

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