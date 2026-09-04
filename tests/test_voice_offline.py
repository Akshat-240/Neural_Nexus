import os
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from voice_offline.generator import generate_pcm_wav, generate_demo_audio_suite
from voice_offline.stt import SpeechToTextEngine
from voice_offline.extractor import FieldEventExtractor
from voice_offline.offline_queue import OfflineQueueManager
from voice_offline.sync_engine import VoiceSyncEngine
from voice_offline.image_processor import ImageEvidenceProcessor
from voice_offline.api import app


class TestVoiceOfflineModule(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        self.wav_path = self.test_dir / "test_audio.wav"
        self.txt_path = self.wav_path.with_suffix(".txt")
        generate_pcm_wav(self.wav_path, duration_sec=2.0)
        self.txt_path.write_text("24-XX spool erected today at Unit 3.", encoding="utf-8")
        
        self.img_path = self.test_dir / "case_A_spool_photo.jpg"
        self.img_path.write_bytes(b"\xFF\xD8\xFF\xE0\x00\x10JFIF\x00\x01\x01\x01\x00\x60\x00\x60\x00\x00\xFF\xD9")

        self.db_path = self.test_dir / "test_queue.db"
        self.queue_mgr = OfflineQueueManager(db_path=self.db_path)
        self.extractor = FieldEventExtractor(default_project_id="PRJ-DEMO-01")
        self.stt = SpeechToTextEngine(engine_type="fallback")
        self.img_processor = ImageEvidenceProcessor()

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_stt_transcription(self):
        res = self.stt.transcribe(str(self.wav_path))
        self.assertIn("raw_text", res)
        self.assertIn("normalized_text", res)
        self.assertIn("24-XX", res["normalized_text"])
        self.assertGreater(res["stt_confidence"], 0.8)

    def test_dynamic_non_hardcoded_fallback(self):
        custom_wav = self.test_dir / "custom_site_recording.wav"
        generate_pcm_wav(custom_wav, duration_sec=1.5)
        # Without sidecar txt and without hardcoded case_a stem
        res = self.stt.transcribe(str(custom_wav))
        self.assertIn("custom site recording", res["raw_text"])

    def test_hinglish_normalization(self):
        hinglish = "Unit 3 par 24-XX spool erection ho gaya hai"
        norm = self.stt.normalize_hinglish(hinglish)
        self.assertIn("at", norm)
        self.assertIn("completed", norm)
        self.assertIn("24-XX", norm)

    def test_field_event_extraction_schema(self):
        text = "24-XX spool erected today at Unit 3."
        event = self.extractor.extract_field_event(
            raw_text=text,
            source_ref="test_voice.wav",
            stt_confidence=0.95
        )
        
        # Canonical schema compliance
        self.assertEqual(event["project_id"], "PRJ-DEMO-01")
        self.assertEqual(event["source"]["type"], "voice")
        self.assertEqual(event["source"]["ref"], "test_voice.wav")
        self.assertEqual(event["raw_text"], text)
        self.assertIsInstance(event["extraction_confidence"], float)
        
        extracted = event["extracted"]
        self.assertEqual(extracted["asset_or_reference"], "24-XX")
        self.assertEqual(extracted["location"], "Unit 3")
        self.assertEqual(extracted["discipline"], "Piping")
        self.assertEqual(extracted["status"], "completed")
        self.assertIsNotNone(extracted["actual_end"])

    def test_image_evidence_processing_schema(self):
        evidence_result = self.img_processor.process_image(
            image_path=str(self.img_path),
            activity_context="24-XX spool erection at Unit 3"
        )
        self.assertIn("evidence_id", evidence_result)
        self.assertEqual(evidence_result["source"]["type"], "image")
        self.assertEqual(evidence_result["source"]["ref"], self.img_path.name)
        
        analysis = evidence_result["analysis"]
        self.assertIn("objects", analysis)
        self.assertIsInstance(analysis["visual_evidence_score"], float)
        self.assertTrue(analysis["supports_activity"])

    def test_offline_sqlite_queue(self):
        event = self.extractor.extract_field_event("24-XX spool erected today at Unit 3.")
        
        # Enqueue
        record = self.queue_mgr.enqueue_event(event)
        self.assertEqual(record["sync_status"], "pending")
        
        # Summary
        summary = self.queue_mgr.get_queue_summary()
        self.assertEqual(summary["pending"], 1)
        self.assertEqual(summary["synced"], 0)
        
        # Get pending
        pending = self.queue_mgr.get_pending_events()
        self.assertEqual(len(pending), 1)
        self.assertEqual(pending[0]["event_id"], event["event_id"])
        
        # Mark synced
        self.queue_mgr.mark_as_synced(event["event_id"])
        summary_after = self.queue_mgr.get_queue_summary()
        self.assertEqual(summary_after["pending"], 0)
        self.assertEqual(summary_after["synced"], 1)

    def test_sync_engine_offline_handling(self):
        event = self.extractor.extract_field_event("24-XX spool erected today at Unit 3.")
        self.queue_mgr.enqueue_event(event)
        
        sync_engine = VoiceSyncEngine(
            queue_manager=self.queue_mgr,
            endpoint_url="http://invalid-host-9999/api/v1/field-events"
        )
        res = sync_engine.sync_pending_events(force=False)
        
        self.assertEqual(res["status"], "offline")
        self.assertEqual(res["remaining_pending"], 1)

    def test_demo_audio_generator(self):
        demo_files = generate_demo_audio_suite()
        self.assertIn("case_a", demo_files)
        self.assertTrue(demo_files["case_a"].exists())


if __name__ == "__main__":
    unittest.main()
