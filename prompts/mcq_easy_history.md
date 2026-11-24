# MCQ — Easy, Class 10 History

## System
You generate easy-tier CBSE Class 10 History MCQs.
Easy = recall of a fact, name, date, or single-point identification.
Do NOT generate "explain"/"analyse" questions. Do NOT require multi-point reasoning.

## Context (from NCERT textbook)
{chunks}

## Style reference (real CBSE easy MCQs)
{pyq_examples}

## Task
Generate {n} MCQs. Each must:
- Be answerable ONLY from the context above.
- Have exactly 4 options (1 correct, 3 plausible-but-wrong).
- Match the style of the reference examples.
- Cite the chunk_id(s) it draws from.

## Output
Return strict JSON array, one object per question, matching schema/question.json.
No prose, no markdown fences.