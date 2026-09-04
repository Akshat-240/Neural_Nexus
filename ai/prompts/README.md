# AI Prompts Module (Person 3)

The `ai/prompts/` module contains the prompt templates, few-shot examples, and JSON output formatting guidelines used by LLMs to parse industrial EPC field reports.

## Structure

- `ai/prompts/extraction_prompts.py`:
  - `EXTRACTION_SYSTEM_PROMPT`: Directs the LLM to act as an EPC Schedule Intelligence AI, enforcing strict domain rules and output schemas.
  - `FEW_SHOT_EXAMPLES`: Ground truth few-shot demonstrations covering piping erection, ambiguous line tasks, and partial percentage progress.
  - `build_extraction_prompt(raw_text, include_few_shot=True)`: Utility that packages the user prompt with domain examples.

## Key Prompt Rules

1. **Anti-Hallucination**: The LLM must not invent line numbers, unit locations, or dates absent from the raw text.
2. **Explicit Status Classification**:
   - Work noted as finished/erected $\rightarrow$ `"status": "completed"`.
   - Work with numeric progress $< 100\%$ $\rightarrow$ `"status": "in_progress"`.
3. **Structured JSON Output**: All responses must parse directly into standard field dictionary keys (`activity`, `discipline`, `status`, `actual_start`, `actual_end`, `location`, `asset_or_reference`, `context`, `progress_pct`, `confidence`).

## Example Prompt Formatting

```python
from ai.prompts.extraction_prompts import build_extraction_prompt

prompt = build_extraction_prompt("24-XX spool erected today at Unit 3.")
print(prompt)
```
