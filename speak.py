# speak.py
import soundfile as sf
import sounddevice as sd
import numpy as np
import tempfile
import os
from kokoro import KPipeline
from config import KOKORO_VOICE, KOKORO_SPEED

# Initialize Kokoro pipeline once at module load
pipeline = KPipeline(lang_code='a', repo_id='hexgrad/Kokoro-82M')

def speak(text: str):
    """
    Convert text to speech using Kokoro and play it immediately.
    Blocks until audio playback is complete.
    """
    if not text or not text.strip():
        return

    print(f"[SONIC]: {text}")

    try:
        audio_chunks = []
        generator = pipeline(text, voice=KOKORO_VOICE, speed=KOKORO_SPEED)

        for i, (gs, ps, audio) in enumerate(generator):
            audio_chunks.append(audio)

        if not audio_chunks:
            print("[speak.py] Warning: No audio generated")
            return

        full_audio = np.concatenate(audio_chunks)
        sd.play(full_audio, samplerate=24000)
        sd.wait()

    except Exception as e:
        print(f"[speak.py] Error: {e}")


if __name__ == "__main__":
    speak("Systems Online. I am Sonic, your personal assistant. How can I help you today, Sir?")
