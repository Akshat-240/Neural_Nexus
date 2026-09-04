import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent

DEFAULT_PROJECT_ID = os.getenv("DEFAULT_PROJECT_ID", "PRJ-DEMO-01")

# Offline Storage
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

AUDIO_STORE_DIR = DATA_DIR / "audio_store"
AUDIO_STORE_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = DATA_DIR / "voice_offline.db"

# API & Sync
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000").rstrip("/")
FIELD_EVENTS_ENDPOINT = f"{BACKEND_URL}/api/v1/field-events"

# STT Configuration
STT_ENGINE = os.getenv("STT_ENGINE", "auto")  # auto | whisper | fallback
DEFAULT_LANGUAGE = os.getenv("DEFAULT_LANGUAGE", "en")
