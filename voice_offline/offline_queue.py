import sqlite3
import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from voice_offline.config import DB_PATH


class OfflineQueueManager:
    """
    Thread-safe SQLite persistent offline queue for voice notes and field events.
    """
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS voice_events (
                    event_id TEXT PRIMARY KEY,
                    project_id TEXT NOT NULL,
                    source_type TEXT NOT NULL,
                    source_ref TEXT,
                    audio_path TEXT,
                    raw_text TEXT NOT NULL,
                    extracted_json TEXT NOT NULL,
                    full_event_json TEXT NOT NULL,
                    extraction_confidence REAL NOT NULL,
                    sync_status TEXT DEFAULT 'pending',
                    retry_count INTEGER DEFAULT 0,
                    last_error TEXT,
                    created_at TEXT NOT NULL,
                    synced_at TEXT
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_sync_status ON voice_events(sync_status)
            """)
            conn.commit()

    def enqueue_event(self, field_event: Dict[str, Any], audio_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Enqueues a canonical Field Event into local SQLite offline storage.
        """
        event_id = field_event["event_id"]
        project_id = field_event["project_id"]
        source_type = field_event.get("source", {}).get("type", "voice")
        source_ref = field_event.get("source", {}).get("ref", "")
        raw_text = field_event["raw_text"]
        extracted_json = json.dumps(field_event["extracted"])
        full_event_json = json.dumps(field_event)
        confidence = field_event["extraction_confidence"]
        created_at = field_event.get("created_at", datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S"))

        with self._get_connection() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO voice_events (
                    event_id, project_id, source_type, source_ref, audio_path,
                    raw_text, extracted_json, full_event_json, extraction_confidence,
                    sync_status, retry_count, last_error, created_at, synced_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending', 0, NULL, ?, NULL)
            """, (
                event_id, project_id, source_type, source_ref, audio_path,
                raw_text, extracted_json, full_event_json, confidence, created_at
            ))
            conn.commit()

        return self.get_event_by_id(event_id)

    def get_event_by_id(self, event_id: str) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT * FROM voice_events WHERE event_id = ?", (event_id,))
            row = cursor.fetchone()
            if row:
                return self._row_to_dict(row)
        return None

    def get_pending_events(self, limit: int = 50) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM voice_events WHERE sync_status = 'pending' ORDER BY created_at ASC LIMIT ?",
                (limit,)
            )
            return [self._row_to_dict(r) for r in cursor.fetchall()]

    def get_all_events(self, limit: int = 100) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM voice_events ORDER BY created_at DESC LIMIT ?",
                (limit,)
            )
            return [self._row_to_dict(r) for r in cursor.fetchall()]

    def mark_as_synced(self, event_id: str, remote_ref: Optional[str] = None) -> bool:
        synced_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")
        with self._get_connection() as conn:
            cursor = conn.execute("""
                UPDATE voice_events
                SET sync_status = 'synced', synced_at = ?, last_error = NULL
                WHERE event_id = ?
            """, (synced_at, event_id))
            conn.commit()
            return cursor.rowcount > 0

    def mark_as_failed(self, event_id: str, error_message: str) -> bool:
        with self._get_connection() as conn:
            cursor = conn.execute("""
                UPDATE voice_events
                SET sync_status = 'failed', retry_count = retry_count + 1, last_error = ?
                WHERE event_id = ?
            """, (error_message, event_id))
            conn.commit()
            return cursor.rowcount > 0

    def get_queue_summary(self) -> Dict[str, int]:
        with self._get_connection() as conn:
            total = conn.execute("SELECT COUNT(*) FROM voice_events").fetchone()[0]
            pending = conn.execute("SELECT COUNT(*) FROM voice_events WHERE sync_status = 'pending'").fetchone()[0]
            synced = conn.execute("SELECT COUNT(*) FROM voice_events WHERE sync_status = 'synced'").fetchone()[0]
            failed = conn.execute("SELECT COUNT(*) FROM voice_events WHERE sync_status = 'failed'").fetchone()[0]
            return {
                "total": total,
                "pending": pending,
                "synced": synced,
                "failed": failed
            }

    def clear_synced_events(self) -> int:
        with self._get_connection() as conn:
            cursor = conn.execute("DELETE FROM voice_events WHERE sync_status = 'synced'")
            conn.commit()
            return cursor.rowcount

    def _row_to_dict(self, row: sqlite3.Row) -> Dict[str, Any]:
        d = dict(row)
        if "full_event_json" in d and d["full_event_json"]:
            d["full_event"] = json.loads(d["full_event_json"])
        if "extracted_json" in d and d["extracted_json"]:
            d["extracted"] = json.loads(d["extracted_json"])
        return d
