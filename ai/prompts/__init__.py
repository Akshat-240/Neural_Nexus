"""Prompts package for AI/ML extraction and matching in Neural Nexus."""

from ai.prompts.extraction_prompts import (
    EXTRACTION_SYSTEM_PROMPT,
    EXTRACTION_USER_PROMPT_TEMPLATE,
    FEW_SHOT_EXAMPLES,
    build_extraction_prompt,
)

__all__ = [
    "EXTRACTION_SYSTEM_PROMPT",
    "EXTRACTION_USER_PROMPT_TEMPLATE",
    "FEW_SHOT_EXAMPLES",
    "build_extraction_prompt",
]
