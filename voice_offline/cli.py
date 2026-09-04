import sys
import argparse
import json
from pathlib import Path

from voice_offline.generator import generate_demo_audio_suite
from voice_offline.stt import SpeechToTextEngine
from voice_offline.extractor import FieldEventExtractor
from voice_offline.offline_queue import OfflineQueueManager
from voice_offline.sync_engine import VoiceSyncEngine


def main():
    parser = argparse.ArgumentParser(description="Neural Nexus Voice Offline Module CLI (Person 5)")
    subparsers = parser.add_subparsers(dest="command", help="Sub-commands")

    # Generate demo command
    subparsers.add_parser("generate-demo", help="Generate synthetic demo audio WAV files for Case A, B, C")

    # Transcribe command
    trans_parser = subparsers.add_parser("transcribe", help="Transcribe audio file or Hinglish text")
    trans_parser.add_argument("--file", "-f", help="Path to audio file (.wav/.mp3)")
    trans_parser.add_argument("--text", "-t", help="Raw voice text note")

    # Process command
    proc_parser = subparsers.add_parser("process", help="Transcribe and convert into canonical Field Event JSON")
    proc_parser.add_argument("--file", "-f", help="Path to audio file (.wav/.mp3)")
    proc_parser.add_argument("--text", "-t", help="Raw voice text note")
    proc_parser.add_argument("--project", "-p", default="PRJ-DEMO-01", help="Project ID")
    proc_parser.add_argument("--enqueue", "-e", action="store_true", help="Automatically enqueue into offline SQLite storage")

    # Queue command
    q_parser = subparsers.add_parser("queue", help="Manage offline SQLite queue")
    q_sub = q_parser.add_subparsers(dest="queue_cmd")
    q_sub.add_parser("list", help="List queued field events")
    q_sub.add_parser("summary", help="Print offline queue statistics")
    q_sub.add_parser("clear-synced", help="Purge synced records from queue")

    # Sync command
    sync_parser = subparsers.add_parser("sync", help="Flush pending offline events to backend API")
    sync_parser.add_argument("--force", action="store_true", help="Force sync attempt regardless of connectivity ping")

    # Serve command
    serve_parser = subparsers.add_parser("serve", help="Launch FastAPI server for Voice Offline module")
    serve_parser.add_argument("--host", default="127.0.0.1", help="Host address")
    serve_parser.add_argument("--port", type=int, default=8005, help="Port number")

    args = parser.parse_args()

    if args.command == "generate-demo":
        paths = generate_demo_audio_suite()
        print("[Success] Generated demo audio files:")
        for case, p in paths.items():
            print(f"  - {case}: {p}")

    elif args.command == "transcribe":
        stt = SpeechToTextEngine()
        if args.file:
            res = stt.transcribe(args.file)
        elif args.text:
            res = {"raw_text": args.text, "normalized_text": stt.normalize_hinglish(args.text)}
        else:
            print("Error: Specify --file or --text")
            sys.exit(1)
        print(json.dumps(res, indent=2))

    elif args.command == "process":
        stt = SpeechToTextEngine()
        extractor = FieldEventExtractor()
        queue_mgr = OfflineQueueManager()

        if args.file:
            stt_res = stt.transcribe(args.file)
            raw = stt_res["normalized_text"]
            source_ref = Path(args.file).name
        elif args.text:
            raw = stt.normalize_hinglish(args.text)
            source_ref = "voice_text_cli"
        else:
            print("Error: Specify --file or --text")
            sys.exit(1)

        field_event = extractor.extract_field_event(
            raw_text=raw,
            source_ref=source_ref,
            project_id=args.project
        )

        if args.enqueue:
            queue_mgr.enqueue_event(field_event, audio_path=args.file)
            print("[Enqueued into SQLite Offline Storage]")

        print(json.dumps(field_event, indent=2))

    elif args.command == "queue":
        queue_mgr = OfflineQueueManager()
        if args.queue_cmd == "summary" or not args.queue_cmd:
            summary = queue_mgr.get_queue_summary()
            print(json.dumps(summary, indent=2))
        elif args.queue_cmd == "list":
            events = queue_mgr.get_all_events()
            print(f"Total Events in Queue: {len(events)}")
            for e in events:
                status = e.get("sync_status", "pending").upper()
                print(f"[{status}] ID: {e['event_id']} | Text: {e['raw_text']} | Confidence: {e['extraction_confidence']}")
        elif args.queue_cmd == "clear-synced":
            count = queue_mgr.clear_synced_events()
            print(f"Cleared {count} synced records.")

    elif args.command == "sync":
        sync_eng = VoiceSyncEngine()
        res = sync_eng.sync_pending_events(force=args.force)
        print(json.dumps(res, indent=2))

    elif args.command == "serve":
        import uvicorn
        print(f"Starting Voice Offline FastAPI server on http://{args.host}:{args.port}")
        uvicorn.run("voice_offline.api:app", host=args.host, port=args.port, reload=True)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
