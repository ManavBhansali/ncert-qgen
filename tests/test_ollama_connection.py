import os
import ollama
import pytest
from dotenv import load_dotenv

load_dotenv()


def test_llm_responds():
    model = os.getenv("LLM_MODEL")
    resp = ollama.chat(
        model=model,
        messages=[{"role": "user", "content": "Reply with exactly: OK"}],
        options={"temperature": 0},
    )
    assert resp["message"]["content"].strip()


def test_embedding_returns_vector():
    model = os.getenv("EMBED_MODEL")
    resp = ollama.embed(model=model, input="Nationalism in India")
    assert len(resp["embeddings"][0]) > 0