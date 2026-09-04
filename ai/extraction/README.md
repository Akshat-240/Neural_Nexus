# AI Extraction Module (Person 3)

The `ai/extraction/` module parses unstructured construction field reports, site engineer logs, and voice transcripts into standardized, schema-compliant `field_event.json` objects.

## Architecture

```text
Raw Field Report ("24-XX spool erected today at Unit 3.")
                   │
                   ▼
       [FieldReportExtractor]
         ├── Online Mode: LLM API (OpenAI-compatible / Gemini)
         └── Offline Fallback: Deterministic Regex & Keyword Parser
                   │
                   ▼
             [Normalizer]
         ├── Discipline Alias Mapping (e.g., "spool" -> "Piping")
         ├── Location Canonicalization (e.g., "u3" -> "Unit 3")
         ├── Asset Tag Normalization (e.g., "Line 24" -> "24-XX")
         ├── Status & Action Mapping ("erected" -> "completed")
         └── Progress Extraction ("50 percent" -> 50.0%)
                   │
                   ▼
       Structured Field Event JSON (contracts/schemas/field_event.json)
```

## Inputs & Outputs

### Input
- `raw_text`: Free-text progress note or transcribed field audio.
- Optional metadata: `event_id`, `project_id`, `source_ref`, `evidence_refs`.

### Output (`contracts/schemas/field_event.json`)
```json
{
  "event_id": "EVT-0001",
  "project_id": "PRJ-DEMO-01",
  "source": {
    "type": "text",
    "ref": "daily_report_case_A"
  },
  "raw_text": "24-XX spool erected today at Unit 3.",
  "extracted": {
    "activity": "24-XX spool erection",
    "discipline": "Piping",
    "status": "completed",
    "actual_start": null,
    "actual_end": "2026-09-04T16:30:00",
    "location": "Unit 3",
    "asset_or_reference": "24-XX",
    "context": "Spool erection"
  },
  "evidence_refs": ["EVD-0001"],
  "extraction_confidence": 0.94,
  "created_at": "2026-09-04T16:31:00Z"
}
```

If partial percentage progress is reported (e.g., Case C), a `progress` object is included:
```json
"progress": {
  "actual_progress_pct": 50.0
}
```

## Fallback & Offline Behavior

- When `prefer_offline=True` or when no LLM API key (`OPENAI_API_KEY` / `LLM_API_KEY`) is set, the extractor uses deterministic EPC pattern recognition.
- Pattern matching guarantees identical, reproducible outputs for standard demo cases:
  - **Case A**: High confidence (`0.94`), identifies asset `24-XX`, discipline `Piping`, status `completed`.
  - **Case B**: Ambiguous line activity (`0.68`), flags unspecified work type.
  - **Case C**: Progress tracking (`0.91`), extracts `50.0%` actual progress.

## Example Usage

```python
from ai.extraction import FieldReportExtractor

# Initialize (offline mode by default)
extractor = FieldReportExtractor(prefer_offline=True)

# Extract structured event
event = extractor.extract(
    raw_text="24-XX spool erected today at Unit 3.",
    event_id="EVT-0001",
    project_id="PRJ-DEMO-01"
)

print(event["extracted"]["activity"])  # "24-XX spool erection"
print(event["extracted"]["discipline"]) # "Piping"
print(event["extraction_confidence"])   # 0.94
```
