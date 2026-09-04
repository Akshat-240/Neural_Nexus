import json
import requests
from typing import Dict, Any, List, Optional
from voice_offline.config import FIELD_EVENTS_ENDPOINT, BACKEND_URL
from voice_offline.offline_queue import OfflineQueueManager


class VoiceSyncEngine:
    """
    Synchronizes offline voice field events with the primary backend API.
    """
    def __init__(self, queue_manager: Optional[OfflineQueueManager] = None, endpoint_url: str = FIELD_EVENTS_ENDPOINT):
        self.queue_manager = queue_manager or OfflineQueueManager()
        self.endpoint_url = endpoint_url

    def check_connectivity(self, timeout: float = 2.0) -> bool:
        """
        Checks if the backend API server is reachable.
        """
        try:
            health_url = f"{BACKEND_URL}/health"
            response = requests.get(health_url, timeout=timeout)
            return response.status_code in (200, 204)
        except Exception:
            try:
                response = requests.options(self.endpoint_url, timeout=timeout)
                return True
            except Exception:
                return False

    def sync_pending_events(self, batch_size: int = 20, force: bool = False) -> Dict[str, Any]:
        """
        Flushes pending events from offline SQLite storage to backend API.
        If force is True, attempts sync even if connectivity ping fails.
        """
        if not force and not self.check_connectivity():
            summary = self.queue_manager.get_queue_summary()
            return {
                "status": "offline",
                "message": "Backend server is unreachable. Events remain safely queued offline.",
                "synced_count": 0,
                "failed_count": 0,
                "remaining_pending": summary["pending"],
                "details": []
            }

        pending = self.queue_manager.get_pending_events(limit=batch_size)
        if not pending:
            summary = self.queue_manager.get_queue_summary()
            return {
                "status": "idle",
                "message": "No pending events to sync.",
                "synced_count": 0,
                "failed_count": 0,
                "remaining_pending": 0,
                "details": []
            }

        synced_count = 0
        failed_count = 0
        details = []

        for record in pending:
            event_id = record["event_id"]
            payload = record.get("full_event") or json.loads(record["full_event_json"])

            try:
                response = requests.post(
                    self.endpoint_url,
                    json=payload,
                    headers={"Content-Type": "application/json"},
                    timeout=5.0
                )
                if response.status_code in (200, 201, 202):
                    self.queue_manager.mark_as_synced(event_id)
                    synced_count += 1
                    details.append({"event_id": event_id, "status": "synced", "http_code": response.status_code})
                else:
                    err_msg = f"HTTP {response.status_code}: {response.text[:100]}"
                    self.queue_manager.mark_as_failed(event_id, err_msg)
                    failed_count += 1
                    details.append({"event_id": event_id, "status": "failed", "error": err_msg})
            except Exception as e:
                err_msg = str(e)
                self.queue_manager.mark_as_failed(event_id, err_msg)
                failed_count += 1
                details.append({"event_id": event_id, "status": "failed", "error": err_msg})

        summary = self.queue_manager.get_queue_summary()
        return {
            "status": "completed",
            "synced_count": synced_count,
            "failed_count": failed_count,
            "remaining_pending": summary["pending"],
            "details": details
        }
