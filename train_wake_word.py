# train_wake_word.py
"""
Train a custom 'Hey Sonic' wake word using OpenWakeWord.
Records positive samples (you saying 'hey sonic') and
negative samples (other speech), then trains a verifier model.

Usage:
    python train_wake_word.py
"""
import os
import sys
import sounddevice as sd
import numpy as np
import soundfile as sf
import time

POSITIVE_DIR = "wake_word_samples/positive"
NEGATIVE_DIR = "wake_word_samples/negative"
SAMPLE_RATE = 16000


def ensure_dirs():
    os.makedirs(POSITIVE_DIR, exist_ok=True)
    os.makedirs(NEGATIVE_DIR, exist_ok=True)


def record_clip(duration=3.0, label=""):
    """Record a single clip and return as numpy array."""
    print(f"[Recording {label}] Speak NOW ({duration}s)...")
    audio = sd.rec(int(duration * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1, dtype='float32')
    sd.wait()
    energy = float(np.abs(audio).mean())
    print(f"  → Got {len(audio)} samples, energy={energy:.6f}")
    return audio


def save_clip(audio, filepath):
    sf.write(filepath, audio, SAMPLE_RATE)


def collect_positive_samples(n=10):
    """Record N positive samples (saying 'hey sonic')."""
    existing = len([f for f in os.listdir(POSITIVE_DIR) if f.endswith('.wav')])
    print(f"\n=== Collecting POSITIVE samples ({n} total, {existing} already exist) ===")
    print("Say 'HEY SONIC' clearly each time.\n")

    count = existing
    while count < existing + n:
        print(f"[{count - existing + 1}/{n}] Say 'HEY SONIC'...")
        input("    Press ENTER to record > ")
        audio = record_clip(duration=3.0, label="hey sonic")
        # Trim to first 1.5s of speech (trim leading silence)
        from scipy.ndimage import uniform_filter1d
        energy_env = uniform_filter1d(np.abs(audio).mean(axis=1), size=500)
        start = np.argmax(energy_env > 0.005)
        end = start + SAMPLE_RATE  # 1 second of audio after trigger
        end = min(end, len(audio))
        if end > start:
            audio = audio[start:end]
        filepath = os.path.join(POSITIVE_DIR, f"positive_{count:03d}.wav")
        save_clip(audio, filepath)
        print(f"  Saved: {filepath}")
        count += 1

    print(f"Positive samples done: {len(os.listdir(POSITIVE_DIR))} total")


def collect_negative_samples(n=10):
    """Record N negative samples (general speech that is NOT 'hey sonic')."""
    existing = len([f for f in os.listdir(NEGATIVE_DIR) if f.endswith('.wav')])
    print(f"\n=== Collecting NEGATIVE samples ({n} total, {existing} already exist) ===")
    print("Say random sentences (NOT 'hey sonic').\n")

    count = existing
    while count < existing + n:
        print(f"[{count - existing + 1}/{n}] Say something else (random speech)...")
        input("    Press ENTER to record > ")
        audio = record_clip(duration=4.0, label="negative")
        # Use full clip for negative
        filepath = os.path.join(NEGATIVE_DIR, f"negative_{count:03d}.wav")
        save_clip(audio, filepath)
        print(f"  Saved: {filepath}")
        count += 1

    print(f"Negative samples done: {len(os.listdir(NEGATIVE_DIR))} total")


def train_model():
    """Train the custom wake word model using OpenWakeWord."""
    import openwakeword
    from sklearn.linear_model import LogisticRegression
    import pickle
    import glob

    print("\n=== Training custom 'Hey Sonic' model ===")

    pos_files = glob.glob(os.path.join(POSITIVE_DIR, "*.wav"))
    neg_files = glob.glob(os.path.join(NEGATIVE_DIR, "*.wav"))

    if len(pos_files) < 5:
        print(f"ERROR: Need at least 5 positive samples, got {len(pos_files)}")
        return False
    if len(neg_files) < 5:
        print(f"ERROR: Need at least 5 negative samples, got {len(neg_files)}")
        return False

    print(f"Positive samples: {len(pos_files)}")
    print(f"Negative samples: {len(neg_files)}")

    output_path = "models/hey_sonic_custom.joblib"
    os.makedirs("models", exist_ok=True)

    print("\nTraining model (this may take a few minutes)...")
    openwakeword.train_custom_verifier(
        positive_reference_clips=POSITIVE_DIR,
        negative_reference_clips=NEGATIVE_DIR,
        output_path=output_path,
        model_name="hey_jarvis",  # base model to adapt
        inference_framework="onnx"
    )

    print(f"\n✅ Custom wake word model saved to: {output_path}")
    print("Update config.py: set CUSTOM_WAKE_MODEL = True")
    return True


if __name__ == "__main__":
    ensure_dirs()

    print("""
╔══════════════════════════════════════════════╗
║  Hey Sonic — Custom Wake Word Trainer        ║
║  Step 1: Record positive samples (hey sonic)║
║  Step 2: Record negative samples (other speech)║
║  Step 3: Train the model                     ║
╚══════════════════════════════════════════════╝
    """)

    action = input("Choose action: [p]ositive samples, [n]egative samples, [t]rain model, [a]ll (p→n→t): ").strip().lower()

    if action in ['p', 'a']:
        n = int(input("How many positive samples? (10 recommended): ").strip() or "10")
        collect_positive_samples(n)

    if action in ['n', 'a']:
        n = int(input("How many negative samples? (10 recommended): ").strip() or "10")
        collect_negative_samples(n)

    if action in ['t', 'a']:
        success = train_model()
        if success:
            print("\n✅ Training complete! Update config.py:")
            print("   Set USE_CUSTOM_WAKE = True")
