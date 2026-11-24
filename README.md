# NCERT Question Generator

A retrieval-augmented generation (RAG) system that generates CBSE-style exam
questions from NCERT textbooks, scoped to a teacher's syllabus and grounded in
the actual textbook text.

## Why this exists
General LLMs generate plausible but ungrounded, unscoped questions. This system
constrains generation to the syllabus portion, grounds every question in a cited
textbook chunk, and verifies that each answer is derivable from the source.

## Scope (v1)
- Class 10, Social Science → History
- Easy difficulty only
- MCQ + 2-mark short answer
- English medium

## Architecture
PDF → chunk+tag → embed+retrieve → generate+verify → (Phase 5: paper assembly)

## Status
- [x] Phase 0: contracts (schemas, config, prompts)
- [ ] Phase 1: ingestion & chunking
- [ ] Phase 2: embedding & retrieval
- [ ] Phase 3: question generation
- [ ] Phase 4: expansion
- [ ] Phase 5: paper assembly

## Quickstart

### Prerequisites
- Python 3.10+
- [Ollama](https://ollama.com) running locally

### Setup
```bash
git clone <your-repo-url>
cd ncert-qgen
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

ollama pull qwen2.5:7b-instruct
ollama pull nomic-embed-text

cp .env.example .env