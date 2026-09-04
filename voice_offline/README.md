# Voice & Offline Field Input Module (Person 5)

> **Neural Nexus — SIH 2026 — PS 26122**  
> **Role Owner**: Person 5 (Voice + Offline Field Input)

## Overview
The **Voice & Offline Field Input Module** eliminates field update friction by allowing field engineers and workers to report site progress via voice recordings or quick Hinglish voice notes—even without an active internet connection.

It transcribes audio, normalizes local jargon (Hinglish/abbreviations), extracts canonical **Field Event** structures matching the team's shared contract (), persists updates safely in a local **SQLite queue**, and automatically synchronizes queued updates when connected to the backend API.

---

## Key Features

1. **Speech-to-Text (STT) Engine** ()
   - Uses local **Whisper** model when available.
   - Includes automatic acoustic/metadata fallback for demo audio notes when running in lightweight environments without Whisper weights.
   - Native WAV/PCM header inspection.

2. **Hinglish & Jargon Normalization** ( & )
   - Converts Indian construction shorthand and Hinglish voice notes into standard English terms:
     - *"Unit 3 par 24-XX spool erection ho gaya hai"* $\rightarrow$ *"24-XX spool erected today at Unit 3."*

3. **Canonical Field Event Extraction** ()
   - Outputs 100% schema-compliant  JSON matching :
     - , , , ,  (, , , , , , , ), , , .

4. **Persistent Offline SQLite Queue** ()
   - SQLite store ().
   - Tracks event status (, , ), retry counters, error logs, and local audio references.

5. **Automatic Backend Sync Engine** ()
   - Checks backend reachability before sending.
   - Flushes pending events to .
   - Handles offline network errors gracefully without data loss.

6. **FastAPI Microservice** ()
   - REST endpoints for frontend & integration layer:
     - 
     - 
     - 
     - 
     - 
     - 

7. **Demo Generator & CLI Tool** ( & )
   - Synthetic 16-bit PCM WAV audio generator for Case A (High Confidence), Case B (Human Review), and Case C (Deviation).
   - Full command-line interface for offline testing and demo presentations.

---

## Directory Structure



---

## Quick Start & CLI Usage

### 1. Generate Synthetic Demo Audio Files
[Success] Generated demo audio files:
  - case_a: /Users/anujsaini/Desktop/sih/voice_offline/data/audio_store/case_a_voice_report.wav
  - case_b: /Users/anujsaini/Desktop/sih/voice_offline/data/audio_store/case_b_voice_report.wav
  - case_c: /Users/anujsaini/Desktop/sih/voice_offline/data/audio_store/case_c_voice_report.wav
*Outputs sample WAV files into  for Case A, Case B, and Case C.*

### 2. Transcribe & Extract a Field Event from Audio
[Enqueued into SQLite Offline Storage]
{
  "event_id": "EVT-VOICE-690503",
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
    "actual_end": "2026-09-04T12:11:43",
    "location": "Unit 3",
    "asset_or_reference": "24-XX",
    "context": "Spool erection at Unit 3"
  },
  "evidence_refs": [
    "EVD-VOICE-7698"
  ],
  "extraction_confidence": 0.93,
  "created_at": "2026-09-04T12:11:43"
}

### 3. Inspect Offline Queue Status
{
  "total": 2,
  "pending": 2,
  "synced": 0,
  "failed": 0
}
Total Events in Queue: 2
[PENDING] ID: EVT-VOICE-690503 | Text: 24-XX spool erected today at Unit 3. | Confidence: 0.93
[PENDING] ID: EVT-VOICE-E0B3AE | Text: 24-XX spool erected today at Unit 3. | Confidence: 0.93

### 4. Sync Queued Events to Backend API
{
  "status": "offline",
  "message": "Backend server is unreachable. Events remain safely queued offline.",
  "synced_count": 0,
  "failed_count": 0,
  "remaining_pending": 2,
  "details": []
}

### 5. Launch FastAPI Dev Server
Starting Voice Offline FastAPI server on http://127.0.0.1:8005
*Access interactive Swagger UI documentation at: *

---

## Testing

Run unit & integration tests using standard Python unittest runner:



---

## Canonical Output Example


