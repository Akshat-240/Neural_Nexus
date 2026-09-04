import os
import shutil
from pathlib import Path
from typing import Dict, Any, Optional, List
from fastapi import FastAPI, APIRouter, File, UploadFile, Form, HTTPException, Query, BackgroundTasks
from pydantic import BaseModel, Field

from voice_offline.config import AUDIO_STORE_DIR, DEFAULT_PROJECT_ID
from voice_offline.stt import SpeechToTextEngine
from voice_offline.extractor import FieldEventExtractor
from voice_offline.offline_queue import OfflineQueueManager
from voice_offline.sync_engine import VoiceSyncEngine

router = APIRouter(prefix="/api/v1/voice", tags=["Voice & Offline Field Input"])

stt_engine = SpeechToTextEngine()
extractor = FieldEventExtractor()
queue_mgr = OfflineQueueManager()
sync_engine = VoiceSyncEngine(queue_manager=queue_mgr)


class TextProcessRequest(BaseModel):
    raw_text: str
    project_id: Optional[str] = DEFAULT_PROJECT_ID
    source_ref: Optional[str] = "voice_text_input"


class QueueSyncRequest(BaseModel):
    force: bool = False
    batch_size: int = 20


@router.post("/transcribe", summary="Transcribe uploaded audio file into text")
async def transcribe_audio(file: UploadFile = File(...), language: Optional[str] = None):
    """
    Upload WAV/MP3/M4A audio file and obtain Speech-to-Text transcription.
    """
    temp_path = AUDIO_STORE_DIR / f"upload_{file.filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    try:
        stt_result = stt_engine.transcribe(str(temp_path), language=language)
        return stt_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription error: {str(e)}")


@router.post("/process", summary="Transcribe audio and extract canonical Field Event")
async def process_voice_event(
    file: Optional[UploadFile] = File(None),
    raw_text: Optional[str] = Form(None),
    project_id: str = Form(DEFAULT_PROJECT_ID)
):
    """
    Accepts audio upload or raw voice text, transcribes, normalizes Hinglish,
    and returns a canonical Field Event object adhering to contracts/schemas/field_event.json.
    """
    if not file and not raw_text:
        raise HTTPException(status_code=400, detail="Provide either an audio file upload or raw_text.")

    if file:
        save_path = AUDIO_STORE_DIR / f"voice_{file.filename}"
        with open(save_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        stt_res = stt_engine.transcribe(str(save_path))
        text_to_extract = stt_res["normalized_text"]
        source_ref = file.filename
        confidence = stt_res["stt_confidence"]
    else:
        text_to_extract = stt_engine.normalize_hinglish(raw_text)
        source_ref = "voice_note_text"
        confidence = 0.95

    field_event = extractor.extract_field_event(
        raw_text=text_to_extract,
        source_ref=source_ref,
        source_type="voice",
        stt_confidence=confidence,
        project_id=project_id
    )
    return field_event


@router.post("/enqueue", summary="Save Field Event into local offline queue")
async def enqueue_field_event(event: Dict[str, Any]):
    """
    Stores a canonical Field Event into local SQLite offline queue when disconnected.
    """
    if "event_id" not in event or "raw_text" not in event:
        raise HTTPException(status_code=400, detail="Invalid Field Event payload format.")

    queued_record = queue_mgr.enqueue_event(event)
    summary = queue_mgr.get_queue_summary()
    return {
        "status": "queued",
        "event_id": event["event_id"],
        "queue_summary": summary,
        "record": queued_record
    }


@router.post("/process-and-queue", summary="Complete voice capture workflow: Transcribe -> Extract -> Enqueue")
async def process_and_queue_voice(
    file: Optional[UploadFile] = File(None),
    raw_text: Optional[str] = Form(None),
    project_id: str = Form(DEFAULT_PROJECT_ID),
    auto_sync: bool = Form(False)
):
    """
    Single-call endpoint for field app: Transcribes voice, extracts Field Event,
    saves to local offline queue, and optionally attempts backend sync.
    """
    field_event = await process_voice_event(file=file, raw_text=raw_text, project_id=project_id)
    audio_path = str(AUDIO_STORE_DIR / f"voice_{Path(file.filename).name}") if file else None

    queued = queue_mgr.enqueue_event(field_event, audio_path=audio_path)
    
    sync_result = None
    if auto_sync:
        sync_result = sync_engine.sync_pending_events(batch_size=5)

    return {
        "field_event": field_event,
        "queue_status": queue_mgr.get_queue_summary(),
        "sync_result": sync_result
    }


@router.post("/sync", summary="Flush offline queue to primary backend API")
async def sync_queue(req: QueueSyncRequest = QueueSyncRequest()):
    """
    Attempts to sync all pending offline field events to backend POST /api/v1/field-events.
    """
    result = sync_engine.sync_pending_events(batch_size=req.batch_size, force=req.force)
    return result


@router.get("/queue", summary="Get offline queue contents and status summary")
async def get_queue_status(status: Optional[str] = Query(None, description="pending | synced | failed | all")):
    """
    Returns summary statistics and list of queued events from local SQLite database.
    """
    summary = queue_mgr.get_queue_summary()
    if status == "pending":
        events = queue_mgr.get_pending_events()
    else:
        events = queue_mgr.get_all_events()

    if status and status != "all" and status != "pending":
        events = [e for e in events if e.get("sync_status") == status]

    return {
        "summary": summary,
        "count": len(events),
        "events": events
    }


# Standalone FastAPI App for independent running/testing
app = FastAPI(
    title="Neural Nexus - Voice Offline Field Input Service",
    version="1.0.0",
    description="Person 5 Voice & Offline Field Input Module API"
)
app.include_router(router)


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok", "module": "voice_offline", "queue": queue_mgr.get_queue_summary()}
