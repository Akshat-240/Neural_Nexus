import os
from voice_offline.stt import SpeechToTextEngine

class VoiceAdapter:
    def __init__(self):
        self.stt = SpeechToTextEngine(engine_type="fallback")

    def transcribe(self, audio_file_path: str) -> str:
        """
        Transcribes the audio file to text.
        """
        result = self.stt.transcribe(audio_file_path)
        return result.get("normalized_text", "")

    def transcribe_and_extract(self, audio_path: str, project_id: str) -> dict:
        """
        Full pipeline to extract an event from a voice note.
        """
        transcript = self.transcribe(audio_path)
        return {"transcript": transcript}
