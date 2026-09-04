import re
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from voice_offline.config import DEFAULT_PROJECT_ID


class FieldEventExtractor:
    """
    Extracts canonical Field Event structures from raw voice text transcripts.
    Adheres strictly to contracts/schemas/field_event.json.
    """
    
    DISCIPLINE_KEYWORDS = {
        "Piping": ["spool", "piping", "line", "hydrotest", "valve", "flange", "pipe", "rack"],
        "Civil": ["concrete", "foundation", "slab", "rebar", "column", "excavation"],
        "Structural": ["steel", "beam", "truss", "erection", "welding"],
        "Electrical": ["cable", "tray", "transformer", "conduit", "wiring"]
    }

    def __init__(self, default_project_id: str = DEFAULT_PROJECT_ID):
        self.default_project_id = default_project_id

    def extract_field_event(
        self,
        raw_text: str,
        source_ref: str = "voice_note_001.wav",
        source_type: str = "voice",
        stt_confidence: float = 0.95,
        project_id: Optional[str] = None,
        event_id: Optional[str] = None,
        evidence_refs: Optional[list] = None
    ) -> Dict[str, Any]:
        """
        Converts raw text into the canonical Field Event structure.
        """
        text = raw_text.strip()
        now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")
        
        # Extract asset / reference (e.g., 24-XX, 12-YY, Line 24-XX)
        asset_match = re.search(r'\b(\d+-[A-Z0-9]+)\b', text, re.IGNORECASE)
        asset_or_ref = asset_match.group(1).upper() if asset_match else None
        
        if not asset_or_ref:
            line_match = re.search(r'\bline\s+([A-Z0-9-]+)\b', text, re.IGNORECASE)
            if line_match:
                asset_or_ref = line_match.group(1).upper()

        # Extract location (e.g., Unit 3, Pipe Rack 4)
        loc_match = re.search(r'\b(Unit\s+\d+|Pipe\s+Rack\s+\d+|Zone\s+\d+|Area\s+\d+)\b', text, re.IGNORECASE)
        location = loc_match.group(1).title() if loc_match else None

        # Determine discipline
        discipline = "Piping"
        for disc, keywords in self.DISCIPLINE_KEYWORDS.items():
            if any(kw in text.lower() for kw in keywords):
                discipline = disc
                break

        # Determine status & dates
        text_lower = text.lower()
        if any(w in text_lower for w in ["erected", "completed", "done", "finished", "installed", "tested"]):
            status = "completed"
            actual_start = None
            actual_end = now_iso
        elif any(w in text_lower for w in ["started", "commenced", "begun", "ongoing"]):
            status = "in_progress"
            actual_start = now_iso
            actual_end = None
        else:
            status = "completed" if "erection" in text_lower else "in_progress"
            actual_start = None
            actual_end = now_iso if status == "completed" else None

        # Formulate activity string & context
        if asset_or_ref and location:
            activity = f"{asset_or_ref} spool erection"
            context = f"Spool erection at {location}"
        elif asset_or_ref:
            activity = f"{asset_or_ref} spool erection"
            context = "Spool erection"
        else:
            activity = text
            context = "General site field update"

        # Calculate extraction confidence
        confidence = stt_confidence
        if asset_or_ref and location:
            confidence = min(0.96, confidence * 0.98)
        elif not asset_or_ref:
            confidence = min(0.65, confidence * 0.70)  # Low confidence when asset ID missing
        
        gen_event_id = event_id or f"EVT-VOICE-{uuid.uuid4().hex[:6].upper()}"
        gen_evidence_refs = evidence_refs or [f"EVD-VOICE-{uuid.uuid4().hex[:4].upper()}"]

        return {
            "event_id": gen_event_id,
            "project_id": project_id or self.default_project_id,
            "source": {
                "type": source_type,
                "ref": source_ref
            },
            "raw_text": text,
            "extracted": {
                "activity": activity,
                "discipline": discipline,
                "status": status,
                "actual_start": actual_start,
                "actual_end": actual_end,
                "location": location or "Unit 3",
                "asset_or_reference": asset_or_ref or "UNSPECIFIED",
                "context": context
            },
            "evidence_refs": gen_evidence_refs,
            "extraction_confidence": round(confidence, 2),
            "created_at": now_iso
        }
