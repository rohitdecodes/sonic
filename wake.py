# wake.py
import numpy as np
import pyaudio
import time
import sounddevice as sd
from openwakeword.model import Model
from config import WAKE_MODEL, WAKE_THRESHOLD, USE_CUSTOM_WAKE, CUSTOM_WAKE_PATH, ASSISTANT_NAME

print(f"[wake.py] Loading wake word model...")
if USE_CUSTOM_WAKE:
    oww_model = Model(
        wakeword_models=[WAKE_MODEL],
        inference_framework="onnx",
        custom_verifier_models={WAKE_MODEL: CUSTOM_WAKE_PATH},
        custom_verifier_threshold=0.5
    )
    print(f"[wake.py] Custom 'Hey Sonic' wake word loaded from {CUSTOM_WAKE_PATH}")
else:
    oww_model = Model(wakeword_models=[WAKE_MODEL], inference_framework="onnx")
    print(f"[wake.py] Wake model ready (built-in: {WAKE_MODEL}).")

CHUNK_SIZE = 1280
SAMPLE_RATE = 16000

# Human-readable wake phrase
WAKE_PHRASE = "Hey Sonic" if USE_CUSTOM_WAKE else f"'{WAKE_MODEL.replace('_', ' ').title()}'"


def wait_for_wake_word() -> bool:
    pa = pyaudio.PyAudio()
    stream = pa.open(
        rate=SAMPLE_RATE,
        channels=1,
        format=pyaudio.paInt16,
        input=True,
        frames_per_buffer=CHUNK_SIZE
    )

    print(f"[SONIC]: Idle — say {WAKE_PHRASE} to wake...")

    try:
        while True:
            raw = stream.read(CHUNK_SIZE, exception_on_overflow=False)
            audio = np.frombuffer(raw, dtype=np.int16)
            prediction = oww_model.predict(audio)

            for model_name, score in prediction.items():
                if score >= WAKE_THRESHOLD:
                    print(f"[SONIC]: Wake detected! (model={model_name}, score={score:.3f})")
                    return True

    except Exception as e:
        print(f"[wake.py] Wake word error: {e}")
        return False

    finally:
        stream.stop_stream()
        stream.close()
        pa.terminate()


def wait_for_clap(claps_needed: int = 2, clap_window: float = 1.5) -> bool:
    CLAP_THRESHOLD = 0.3
    MIN_CLAP_GAP = 0.15

    clap_times = []
    print(f"[SONIC]: Idle — clap {claps_needed} times to wake...")

    def audio_callback(indata, frames, time_info, status):
        energy = float(np.abs(indata).max())
        now = time.time()
        if energy > CLAP_THRESHOLD:
            if not clap_times or (now - clap_times[-1]) > MIN_CLAP_GAP:
                clap_times.append(now)
                print(f"[wake.py] Clap {len(clap_times)} (energy={energy:.3f})")

    with sd.InputStream(callback=audio_callback, channels=1,
                        samplerate=44100, blocksize=1024):
        while True:
            time.sleep(0.05)
            now = time.time()
            clap_times[:] = [t for t in clap_times if now - t <= clap_window]
            if len(clap_times) >= claps_needed:
                print("[SONIC]: Clap sequence detected!")
                return True


if __name__ == "__main__":
    print(f"Testing wake word — say {WAKE_PHRASE}...")
    result = wait_for_wake_word()
    if result:
        print("Wake word test PASSED!")
