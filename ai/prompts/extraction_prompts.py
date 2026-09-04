"""Prompt templates and formatters for field report structured extraction."""

import json

EXTRACTION_SYSTEM_PROMPT = """You are an expert EPC (Engineering, Procurement, Construction) Schedule Intelligence AI.
Your task is to analyze unstructured field notes and daily progress reports from construction job sites and extract structured work event details.

You must extract the following fields strictly into a JSON object:
- "activity": Concise description of the construction task performed (e.g., "24-XX spool erection", "Pipe support installation").
- "discipline": Engineering discipline. Choose from ["Piping", "Mechanical", "Civil", "Electrical", "Instrumentation", "Structural"].
- "actual_start": ISO8601 timestamp string if mentioned, or null.
- "actual_end": ISO8601 timestamp string if explicitly mentioned, or null.
- "location": Job site location, unit, plant, or area (e.g., "Unit 3", "Area 5", "Pipe Rack B").
- "context": Additional context summarizing the activity and scope.
- "progress_pct": Numerical percentage progress if explicitly specified in the text (e.g., 50.0 for 50%), or null if unspecified.
- "confidence": Float between 0.0 and 1.0 indicating your confidence in the extraction based on specificity of details.

Rules:
1. Do not hallucinate line numbers, locations, or dates that are not in the raw text.
2. If an activity is completed, status must be "completed".
3. If partial percentage is reported (e.g., "50 percent complete"), status must be "in_progress" and progress_pct must be the numeric value.
4. If details are ambiguous or missing, lower the confidence score.
5. Return ONLY a valid JSON object without markdown fences or extraneous text.
"""

FEW_SHOT_EXAMPLES = [
    {
        "raw_text": "24-XX spool erected today at Unit 3.",
        "extracted": {
            "activity": "24-XX spool erection",
            "discipline": "Piping",
            "status": "completed",
            "actual_start": None,
            "actual_end": "2026-09-03T16:30:00",
            "location": "Unit 3",
            "asset_or_reference": "24-XX",
            "context": "Spool erection",
            "progress_pct": 100.0,
            "confidence": 0.94
        }
    },
    {
        "raw_text": "Line 24 work completed.",
        "extracted": {
            "activity": "Line 24 work",
            "discipline": "Piping",
            "status": "completed",
            "actual_start": None,
            "actual_end": "2026-09-03T17:00:00",
            "location": "Unit 3",
            "asset_or_reference": "24-XX",
            "context": "Unspecified Line 24 work",
            "progress_pct": 100.0,
            "confidence": 0.68
        }
    },
    {
        "raw_text": "Pipe support installation is approximately 50 percent complete at Unit 3.",
        "extracted": {
            "activity": "Pipe support installation",
            "discipline": "Mechanical",
            "status": "in_progress",
            "actual_start": None,
            "actual_end": None,
            "location": "Unit 3",
            "asset_or_reference": None,
            "context": "Pipe support installation",
            "progress_pct": 50.0,
            "confidence": 0.91
        }
    }
]

EXTRACTION_USER_PROMPT_TEMPLATE = """Analyze the following field report text and extract the structured construction activity details:

Raw Field Text:
"{raw_text}"

Return the structured extraction as a single JSON object.
"""


def build_extraction_prompt(raw_text: str, include_few_shot: bool = True) -> str:
    """Builds the full user prompt for LLM extraction.

    Args:
        raw_text: Unstructured construction report text.
        include_few_shot: Whether to prepend few-shot examples.

    Returns:
        Formatted prompt string.
    """
    prompt_parts = []
    if include_few_shot:
        prompt_parts.append("Here are examples of expected extractions:\n")
        for i, ex in enumerate(FEW_SHOT_EXAMPLES, 1):
            prompt_parts.append(f"Example {i}:\nInput: \"{ex['raw_text']}\"\nOutput:\n{json.dumps(ex['extracted'], indent=2)}\n")
        prompt_parts.append("Now extract from the following:\n")

    prompt_parts.append(EXTRACTION_USER_PROMPT_TEMPLATE.format(raw_text=raw_text.strip()))
    return "\n".join(prompt_parts)
