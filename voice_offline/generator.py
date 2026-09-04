import wave
import struct
import math
from pathlib import Path
from typing import Dict
from voice_offline.config import AUDIO_STORE_DIR


DEMO_SPEECH_TEXTS = {
    "case_a": "24-XX spool erected today at Unit 3.",
    "case_b": "Piping work near unit 3 done.",
    "case_c": "Line 24-XX erection started today at Unit 3."
}


def generate_pcm_wav(output_path: Path, duration_sec: float = 3.0, sample_rate: int = 16000) -> Path:
    """
    Generates a valid 16-bit PCM mono WAV file natively with Python stdlib wave module.
    Produces a comfortable acoustic tone pattern representing synthesized voice data.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    num_samples = int(duration_sec * sample_rate)
    
    with wave.open(str(output_path), 'wb') as wf:
        wf.setnchannels(1)      # Mono
        wf.setsampwidth(2)      # 16-bit PCM (2 bytes)
        wf.setframerate(sample_rate)
        
        frames = []
        for i in range(num_samples):
            t = float(i) / sample_rate
            # Synthesize voice-like multi-frequency acoustic signal
            val = int(
                4000.0 * math.sin(2.0 * math.pi * 220.0 * t) +
                2000.0 * math.sin(2.0 * math.pi * 440.0 * t) +
                1000.0 * math.sin(2.0 * math.pi * 880.0 * t)
            )
            # Clip 16-bit signed integer boundaries
            val = max(-32768, min(32767, val))
            frames.append(struct.pack('<h', val))
            
        wf.writeframes(b''.join(frames))
        
    return output_path


def generate_demo_audio_suite() -> Dict[str, Path]:
    """
    Generates demo audio files (.wav) and transcript sidecars (.txt) for the 3 required SIH demo cases.
    """
    generated_files = {}
    
    for case_id, text in DEMO_SPEECH_TEXTS.items():
        wav_filename = f"{case_id}_voice_report.wav"
        wav_path = AUDIO_STORE_DIR / wav_filename
        txt_path = wav_path.with_suffix(".txt")
        
        generate_pcm_wav(wav_path, duration_sec=3.5)
        txt_path.write_text(text, encoding="utf-8")
        
        generated_files[case_id] = wav_path
        
    return generated_files


if __name__ == "__main__":
    paths = generate_demo_audio_suite()
    print("Demo audio files generated:", paths)
