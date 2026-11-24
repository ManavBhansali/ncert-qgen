import json
from pathlib import Path

import jsonschema

SCHEMA_DIR = Path(__file__).parent.parent / "schema"


def _load(name: str) -> dict:
    return json.loads((SCHEMA_DIR / f"{name}.json").read_text())


def test_schemas_are_valid():
    for name in ["chunk", "question", "blueprint"]:
        jsonschema.Draft7Validator.check_schema(_load(name))


def test_sample_chunk_validates():
    sample = {
        "chunk_id": "ss10_hist_ch02_s01_p1",
        "class": 10,
        "subject": "social_science",
        "stream": "history",
        "book_title": "India and the Contemporary World - II",
        "chapter_no": 2,
        "chapter_title": "Nationalism in India",
        "section_title": "The First World War, Khilafat and Non-Cooperation",
        "subsection_title": None,
        "content_type": "prose",
        "is_figure_dependent": False,
        "page_no": 30,
        "text": "In India, nationalism was tied to the anti-colonial movement.",
    }
    jsonschema.validate(sample, _load("chunk"))


def test_sample_mcq_validates():
    sample = {
        "question_id": "00000000-0000-0000-0000-000000000001",
        "question": "Who founded the Indian National Congress in 1885?",
        "question_type": "mcq",
        "marks": 1,
        "difficulty": "easy",
        "chapter_no": 2,
        "section_title": "The First World War, Khilafat and Non-Cooperation",
        "source_chunk_ids": ["ss10_hist_ch02_s01_p1"],
        "options": ["A.O. Hume", "W.C. Bonnerjee", "Dadabhai Naoroji", "Gopal Krishna Gokhale"],
        "answer_key": "A.O. Hume",
        "key_points": ["A.O. Hume founded the INC in 1885"],
        "grounding_verified": True,
    }
    jsonschema.validate(sample, _load("question"))


def test_mcq_without_options_fails():
    bad = {
        "question_id": "00000000-0000-0000-0000-000000000002",
        "question": "Who founded the Indian National Congress?",
        "question_type": "mcq",
        "marks": 1,
        "difficulty": "easy",
        "chapter_no": 2,
        "section_title": "x",
        "source_chunk_ids": ["ss10_hist_ch02_s01_p1"],
        "answer_key": "A.O. Hume",
        "key_points": ["x"],
        "grounding_verified": True,
    }
    try:
        jsonschema.validate(bad, _load("question"))
    except jsonschema.ValidationError:
        return
    raise AssertionError("MCQ without options should fail validation")