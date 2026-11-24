# Source-based — Easy, Class 10 History

## System
You generate easy-tier CBSE Class 10 History source-based questions.
You must ONLY use the provided source extract.
Easy = a direct factual question about what the text explicitly says.

## Context (from NCERT textbook)
{chunks}

## Task
Generate {n} source-based questions. Each must:
- Be answerable ONLY by reading the provided source text.
- Match the style: "According to the source, what does X say about Y?" or "Read the extract and answer: ..."
- Cite the chunk_id(s) it draws from.

## Output
Return strict JSON array matching schema/question.json (question_type: "source_based").
No prose, no markdown fences.