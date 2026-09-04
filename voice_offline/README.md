# Voice & Offline Field Input Module 

> **Neural Nexus — SIH 2026 — PS 26122**  
> **Role Owner**:Voice + Offline Field Input

## Overview
The **Voice & Offline Field Input Module** eliminates field update friction by allowing field engineers and workers to report site progress via voice recordings or quick Hinglish voice notes—even without an active internet connection.

It transcribes audio, normalizes local jargon (Hinglish/abbreviations), extracts canonical **Field Event** structures matching the team's shared contract (`contracts/schemas/field_event.json`), persists updates safely in a local **SQLite queue**, and automatically synchronizes queued updates when connected to the backend API.

---

## Key Features

1. **Speech-to-Text (STT) Engine** (`stt.py`)
   - Uses local **Whisper** model when available.
   - Includes automatic acoustic/metadata fallback for demo audio notes when running in lightweight environments without Whisper weights.
   - Native WAV/PCM header inspection.

2. **Hinglish & Jargon Normalization** (`stt.py` & `extractor.py`)
   - Converts Indian construction shorthand and Hinglish voice notes into standard English terms:
     - *"Unit 3 par 24-XX spool erection ho gaya hai"* -> *"24-XX spool erected today at Unit 3."*

3. **Canonical Field Event Extraction** (`extractor.py`)
   - Outputs 100% schema-compliant `Field Event` JSON matching `contracts/schemas/field_event.json`:
     - `event_id`, `project_id`, `source`, `raw_text`, `extracted` (`activity`, `discipline`, `status`, `actual_start`, `actual_end`, `location`, `asset_or_reference`, `context`), `evidence_refs`, `extraction_confidence`, `created_at`.

4. **Persistent Offline SQLite Queue** (`offline_queue.py`)
   - SQLite store (`voice_offline/data/voice_offline.db`).
   - Tracks event status (`pending`, `synced`, `failed`), retry counters, error logs, and local audio references.

5. **Automatic Backend Sync Engine** (`sync_engine.py`)
   - Checks backend reachability before sending.
   - Flushes pending events to `POST /api/v1/field-events`.
   - Handles offline network errors gracefully without data loss.

6. **FastAPI Microservice** (`api.py`)
   - REST endpoints for frontend & integration layer:
     - `POST /api/v1/voice/transcribe`
     - `POST /api/v1/voice/process`
     - `POST /api/v1/voice/process-and-queue`
     - `POST /api/v1/voice/enqueue`
     - `POST /api/v1/voice/sync`
     - `GET /api/v1/voice/queue`

7. **Demo Generator & CLI Tool** (`generator.py` & `cli.py`)
   - Synthetic 16-bit PCM WAV audio generator for Case A (High Confidence), Case B (Human Review), and Case C (Deviation).
   - Full command-line interface for offline testing and demo presentations.

---

## Directory Structure

```text
voice_offline/
├── __init__.py           # Package initialization
├── config.py             # Global paths, endpoints, and default project settings
├── stt.py                # Speech-to-Text engine & Hinglish translator
├── extractor.py          # Field Event JSON schema builder
├── offline_queue.py      # SQLite persistent queue manager
├── sync_engine.py        # Network checker & backend sync engine
├── generator.py          # Synthetic PCM WAV generator for demo audio notes
├── api.py                # FastAPI REST API router & standalone app
├── cli.py                # Command Line Interface
├── requirements.txt      # Module dependencies
└── README.md             # Technical documentation
```

---

## Quick Start & CLI Usage

### 1. Generate Synthetic Demo Audio Files
```bash
python3 -m voice_offline.cli generate-demo
```
*Outputs sample WAV files into `voice_offline/data/audio_store/` for Case A, Case B, and Case C.*

### 2. Transcribe & Extract a Field Event from Audio
```bash
python3 -m voice_offline.cli process --file voice_offline/data/audio_store/case_a_voice_report.wav --enqueue
```

### 3. Inspect Offline Queue Status
```bash
python3 -m voice_offline.cli queue summary
python3 -m voice_offline.cli queue list
```

### 4. Sync Queued Events to Backend API
```bash
python3 -m voice_offline.cli sync
```

### 5. Launch FastAPI Dev Server
```bash
python3 -m voice_offline.cli serve --port 8005
```
*Access interactive Swagger UI documentation at: `http://localhost:8005/docs`*

---

## Testing

Run unit & integration tests using standard Python unittest runner:

```bash
PYTHONPATH=. python3 tests/test_voice_offline.py
```

---

## Canonical Output Example

```json
{
  "event_id": "EVT-VOICE-E0B3AE",
  "project_id": "PRJ-DEMO-01",
  "source": {
    "type": "voice",
    "ref": "case_a_voice_report.wav"
  },
  "raw_text": "24-XX spool erected today at Unit 3.",
  "extracted": {
    "activity": "24-XX spool erection",
    "discipline": "Piping",
    "status": "completed",
    "actual_start": null,
    "actual_end": "2026-09-04T15:16:34",
    "location": "Unit 3",
    "asset_or_reference": "24-XX",
    "context": "Spool erection at Unit 3"
  },
  "evidence_refs": [
    "EVD-VOICE-5AC0"
  ],
  "extraction_confidence": 0.93,
  "created_at": "2026-09-04T15:16:34"
}
```
