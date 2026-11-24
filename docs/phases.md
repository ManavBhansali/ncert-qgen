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