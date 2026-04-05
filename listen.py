# listen.py
import whisper
import sounddevice as sd
import numpy as np
import tempfile
import soundfile as sf
import torch
import os
from config import WHISPER_MODEL

device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"[listen.py] Loading Whisper ({WHISPER_MODEL}) on {device}...")
model = whisper.load_model(WHISPER_MODEL, device=device)
print(f"[listen.py] Whisper ready.")

SAMPLE_RATE = 16000
CHANNELS = 1
MAX_RECORD_SECONDS = 15

def record_until_silence() -> np.ndarray:
    print("[SONIC]: Listening...")

    recorded_frames = []
    silent_frames = 0
    frames_per_check = int(SAMPLE_RATE * 0.1)
    # Wait for 2.0 seconds of silence before stopping
    silence_limit = int(2.0 / 0.1)
    max_frames = int(MAX_RECORD_SECONDS / 0.1)
    total_frames = 0

    with sd.InputStream(samplerate=SAMPLE_RATE, channels=CHANNELS, dtype='float32') as stream:
        while total_frames < max_frames:
            chunk, _ = stream.read(frames_per_check)
            recorded_frames.append(chunk.copy())
            total_frames += 1

            energy = np.abs(chunk).mean()
            if energy < 0.005:  # Lower threshold = catches quieter speech
                silent_frames += 1
            else:
                silent_frames = 0

            # Only stop if we have at least 5 frames of audio AND 2s of silence
            if silent_frames >= silence_limit and total_frames > 10:
                break

    audio = np.concatenate(recorded_frames, axis=0).flatten()
    # Convert to int16 for Whisper
    audio = (audio * 32767).astype(np.int16)
    print(f"[listen.py] Recorded {len(audio)/SAMPLE_RATE:.1f}s of audio")
    return audio


def transcribe(audio: np.ndarray) -> str:
    if audio is None or len(audio) == 0:
        return ""

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        temp_path = f.name
        sf.write(temp_path, audio, SAMPLE_RATE)

    try:
        result = model.transcribe(temp_path, language="en", fp16=torch.cuda.is_available())
        text = result["text"].strip()
        if text:
            print(f"[YOU]: {text}")
        return text
    except Exception as e:
        print(f"[listen.py] Transcription error: {e}")
        return ""
    finally:
        try:
            os.unlink(temp_path)
        except:
            pass


def listen() -> str:
    audio = record_until_silence()
    return transcribe(audio)


if __name__ == "__main__":
    print("Say something...")
    result = listen()
    print(f"Transcribed: '{result}'")
