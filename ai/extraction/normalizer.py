"""Normalization module for construction terms, disciplines, locations, assets, and progress."""

import re
from typing import Any, Dict, Optional, Tuple

# Canonical discipline mappings
DISCIPLINE_MAP = {
    "piping": "Piping",
    "pipe": "Piping",
    "spool": "Piping",
    "spool erection": "Piping",
    "pipe erection": "Piping",
    "hydrotest": "Piping",
    "tie-in": "Piping",
    "flange": "Piping",
    "valve": "Piping",
    "mechanical": "Mechanical",
    "support": "Mechanical",
    "pipe support": "Mechanical",
    "supports": "Mechanical",
    "hanger": "Mechanical",
    "pump": "Mechanical",
    "compressor": "Mechanical",
    "vessel": "Mechanical",
    "equipment": "Mechanical",
    "civil": "Civil",
    "concrete": "Civil",
    "excavation": "Civil",
    "foundation": "Civil",
    "paving": "Civil",
    "electrical": "Electrical",
    "cable": "Electrical",
    "conduit": "Electrical",
    "tray": "Electrical",
    "substation": "Electrical",
    "transformer": "Electrical",
    "instrumentation": "Instrumentation",
    "sensor": "Instrumentation",
    "transmitter": "Instrumentation",
    "tubing": "Instrumentation",
    "calibration": "Instrumentation",
    "structural": "Structural",
    "steel": "Structural",
    "structure": "Structural",
    "framing": "Structural",
}

# Location canonicalization regexes
LOCATION_ALIASES = {
    r"\bu[-_ ]?3\b|\bunit[-_ ]*#?3\b": "Unit 3",
    r"\bu[-_ ]?1\b|\bunit[-_ ]*#?1\b": "Unit 1",
    r"\bu[-_ ]?2\b|\bunit[-_ ]*#?2\b": "Unit 2",
    r"\bu[-_ ]?4\b|\bunit[-_ ]*#?4\b": "Unit 4",
    r"\barea[-_ ]*#?(\d+)\b": r"Area \1",
    r"\bpipe[-_ ]*rack[-_ ]*([a-zA-Z0-9]+)\b": r"Pipe Rack \1",
}

# Asset / Line tag mappings
# In industrial EPC demo schedules, "Line 24", "Line-24", "L-24" corresponds to "24-XX"
LINE_TAG_PATTERNS = [
    (re.compile(r"\b24-XX\b", re.IGNORECASE), "24-XX"),
    (re.compile(r"\bline[-_ ]*24(?:-xx)?\b", re.IGNORECASE), "24-XX"),
    (re.compile(r"\bl-24\b", re.IGNORECASE), "24-XX"),
]

# Status keywords
COMPLETION_KEYWORDS = [
    "erected", "completed", "installed", "finished", "done", "handed over", "boxed up"
]
IN_PROGRESS_KEYWORDS = [
    "in progress", "ongoing", "underway", "approximately", "installing", "working", "started", "partially"
]


def normalize_discipline(text: Optional[str]) -> str:
    """Maps free-text discipline description or context to standard EPC discipline name.

    Args:
        text: Free-text discipline or activity term.

    Returns:
        Canonical discipline name (defaults to 'Piping' or 'General' if unrecognized).
    """
    if not text:
        return "General"

    lower = text.strip().lower()
    if lower in DISCIPLINE_MAP:
        return DISCIPLINE_MAP[lower]

    for keyword, canonical in DISCIPLINE_MAP.items():
        if keyword in lower:
            return canonical

    return text.strip().capitalize()


def normalize_location(text: Optional[str]) -> Optional[str]:
    """Standardizes plant and site location identifiers (e.g., 'u3' -> 'Unit 3').

    Args:
        text: Raw location string.

    Returns:
        Standardized location string, or None if no location pattern matches.
    """
    if not text:
        return None

    cleaned = text.strip()
    for pattern, canonical in LOCATION_ALIASES.items():
        if re.search(pattern, cleaned, re.IGNORECASE):
            if "\\" in canonical:
                return re.sub(pattern, canonical, cleaned, flags=re.IGNORECASE)
            return canonical

    return None


def extract_and_normalize_asset(text: Optional[str]) -> Optional[str]:
    """Identifies and normalizes asset, line, or spool tag from text (e.g. 'Line 24' -> '24-XX').

    Args:
        text: Text containing potential line or asset reference.

    Returns:
        Canonical asset reference (e.g. '24-XX') or None if not found.
    """
    if not text:
        return None

    for pattern, canonical in LINE_TAG_PATTERNS:
        if pattern.search(text):
            return canonical

    # Generic pattern for tag numbers like "P-101", "V-2001", "PIP-1024"
    match = re.search(r"\b([A-Z]{1,4}-\d{2,5}[A-Z]?)\b", text)
    if match:
        return match.group(1).upper()

    return None


def extract_progress_pct(text: Optional[str]) -> Optional[float]:
    """Extracts numerical progress percentage from text if mentioned.

    Examples:
        '50 percent complete' -> 50.0
        'approx 75%' -> 75.0

    Args:
        text: Raw text string.

    Returns:
        Float value between 0.0 and 100.0, or None.
    """
    if not text:
        return None

    # Match patterns like: "50 percent", "50%", "50.5 %", "fifty percent"
    word_num_map = {"fifty": 50.0, "twenty five": 25.0, "seventy five": 75.0, "hundred": 100.0}
    for word_val, num_val in word_num_map.items():
        if f"{word_val} percent" in text.lower():
            return num_val

    match = re.search(r"(\d+(?:\.\d+)?)\s*(?:%|percent)", text, re.IGNORECASE)
    if match:
        try:
            val = float(match.group(1))
            return max(0.0, min(100.0, val))
        except ValueError:
            pass

    return None


def normalize_status(text: Optional[str], progress_pct: Optional[float] = None) -> str:
    """Infers standardized activity status: 'completed', 'in_progress', or 'not_started'.

    Args:
        text: Raw text describing activity.
        progress_pct: Extracted numeric progress percentage.

    Returns:
        Standardized status string.
    """
    if progress_pct is not None:
        if progress_pct >= 100.0:
            return "completed"
        elif progress_pct > 0.0:
            return "in_progress"
        else:
            return "not_started"

    if not text:
        return "in_progress"

    lower = text.lower()
    for kw in COMPLETION_KEYWORDS:
        if re.search(rf"\b{kw}\b", lower):
            return "completed"

    for kw in IN_PROGRESS_KEYWORDS:
        if re.search(rf"\b{kw}\b", lower):
            return "in_progress"

    return "in_progress"


def normalize_field_event_data(extracted: Dict[str, Any], raw_text: str = "") -> Tuple[Dict[str, Any], Optional[Dict[str, float]]]:
    """Applies all normalization rules to the extracted fields.

    Args:
        extracted: Raw extracted dictionary from LLM or regex.
        raw_text: Original raw field report text for fallback inference.

    Returns:
        Tuple of (normalized_extracted_dict, progress_dict_or_none)
    """
    combined_text = f"{raw_text} {extracted.get('activity', '')} {extracted.get('context', '')}".strip()

    # Normalize progress percentage
    pct = extracted.get("progress_pct")
    if pct is None or not isinstance(pct, (int, float)):
        pct = extract_progress_pct(combined_text)

    # Normalize status
    raw_status = extracted.get("status")
    status = normalize_status(raw_status or combined_text, progress_pct=pct)

    # Normalize discipline
    raw_discipline = extracted.get("discipline")
    discipline = normalize_discipline(raw_discipline or combined_text)

    # Normalize location
    raw_location = extracted.get("location")
    location = normalize_location(raw_location) or normalize_location(combined_text)
    # Normalize asset/reference
    raw_asset = extracted.get("asset_or_reference")
    asset = extract_and_normalize_asset(raw_asset) or extract_and_normalize_asset(combined_text)

    # Clean activity description
    activity = extracted.get("activity")
    if not activity:
        if asset:
            activity = f"{asset} work"
        else:
            activity = "General field work"
    activity = activity.strip()

    context = extracted.get("context") or activity

    # Build normalized extracted payload
    normalized_extracted = {
        "activity": activity,
        "discipline": discipline,
        "status": status,
        "actual_start": extracted.get("actual_start"),
        "actual_end": extracted.get("actual_end"),
        "location": location,
        "asset_or_reference": asset,
        "context": context,
    }

    progress_payload = None
    if pct is not None:
        progress_payload = {"actual_progress_pct": float(pct)}
    elif status == "completed":
        progress_payload = {"actual_progress_pct": 100.0}

    return normalized_extracted, progress_payload
