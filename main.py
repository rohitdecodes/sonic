# main.py — Day 2 final version
import time
import datetime
import os
import threading
from wake import wait_for_wake_word
from listen import listen
from brain import think, reset_conversation, get_plan_summary
from speak import speak
from spotify_control import play_music, pause_music, next_track, get_current_track
from config import (
    USER_TITLE, ASSISTANT_NAME, SILENCE_TIMEOUT, LOG_FILE,
    SPOTIFY_DEFAULT_PLAYLIST
)

os.makedirs("logs", exist_ok=True)


def log(message: str):
    """Append timestamped message to session log."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")


def rotate_log():
    """
    Keep only the last 500 lines in session.log.
    Called once at startup — prevents unbounded log growth.
    """
    if not os.path.exists(LOG_FILE):
        return
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
        if len(lines) > 500:
            with open(LOG_FILE, "w", encoding="utf-8") as f:
                f.writelines(lines[-500:])
            print(f"[main] Log rotated — kept last 500 lines")
    except Exception as e:
        print(f"[main] Log rotation error: {e}")


def get_time_greeting() -> str:
    hour = datetime.datetime.now().hour
    if hour < 12:
        return "Good morning"
    elif hour < 17:
        return "Good afternoon"
    elif hour < 21:
        return "Good evening"
    else:
        return "Good night"


def wake_greeting():
    """
    Full wake sequence:
    1. Greet with time of day
    2. Read out today's plan summary (via Groq)
    3. Start Spotify music in background (non-blocking)
    """
    greeting = get_time_greeting()

    # Step 1 — greet
    speak(f"{greeting}, {USER_TITLE}. {ASSISTANT_NAME} is online.")

    # Step 2 — plan summary
    speak("Here is your plan for today.")
    plan_summary = get_plan_summary()
    speak(plan_summary)

    # Step 3 — start Spotify in a background thread so it doesn't block voice
    def start_music():
        success = play_music()
        if success:
            print("[main] Spotify playback started.")
        else:
            print("[main] Spotify unavailable — no active device.")

    music_thread = threading.Thread(target=start_music, daemon=True)
    music_thread.start()

    speak(f"How can I assist you, {USER_TITLE}?")


def handle_spotify_commands(text: str) -> bool:
    """
    Check if user issued a Spotify voice command.
    Returns True if handled (so main loop doesn't send to Groq).
    """
    text_lower = text.lower()

    if any(p in text_lower for p in ["pause music", "stop music", "mute music"]):
        pause_music()
        speak("Music paused, Sir.")
        return True

    if any(p in text_lower for p in ["play music", "resume music", "start music"]):
        play_music()
        speak("Resuming music, Sir.")
        return True

    if any(p in text_lower for p in ["next song", "skip song", "next track"]):
        next_track()
        speak("Skipping to next track, Sir.")
        return True

    if any(p in text_lower for p in ["what's playing", "what is playing", "current song"]):
        track = get_current_track()
        speak(f"Currently playing: {track}")
        return True

    return False  # Not a Spotify command — pass to Groq


def is_shutdown_command(text: str) -> bool:
    shutdown_phrases = [
        "goodbye sonic", "bye sonic", "shut down", "shutdown",
        "that's all", "thats all", "go to sleep", "sleep mode",
        "goodbye jarvis", "bye jarvis"
    ]
    return any(phrase in text.lower() for phrase in shutdown_phrases)


def run():
    """
    Main SONIC loop — full Day 2 state machine.

    IDLE     → passively listening for wake word
    AWAKE    → morning greeting + plan summary + Spotify
    LOOP     → listen → Spotify command check → Groq → speak → repeat
    SHUTDOWN → graceful exit on command or silence timeout
    """
    print("""
╔══════════════════════════════════════════╗
║   S.O.N.I.C. — Day 2                    ║
║   Systems-Oriented Neural                ║
║   Intelligence Companion                 ║
║                                          ║
║   Say "Hey Jarvis" to wake               ║
║   Say "goodbye sonic" to sleep           ║
╚══════════════════════════════════════════╝
    """)

    rotate_log()
    log("=== SONIC session started ===")

    while True:
        # ── IDLE ──────────────────────────────────────────────────────────────
        wait_for_wake_word()

        # ── AWAKE ─────────────────────────────────────────────────────────────
        reset_conversation()
        log("Wake word detected")
        wake_greeting()
        last_interaction = time.time()

        # ── CONVERSATION LOOP ─────────────────────────────────────────────────
        while True:

            # Silence timeout — return to idle
            if time.time() - last_interaction > SILENCE_TIMEOUT:
                speak(f"Going idle, {USER_TITLE}. Say Hey Jarvis when you need me.")
                log("Session ended — silence timeout")
                break

            # ── LISTEN ────────────────────────────────────────────────────────
            user_input = listen()

            if not user_input or not user_input.strip():
                continue

            log(f"USER: {user_input}")
            last_interaction = time.time()

            # ── SHUTDOWN CHECK ────────────────────────────────────────────────
            if is_shutdown_command(user_input):
                pause_music()
                speak(f"Understood, {USER_TITLE}. Shutting down. Have a productive session.")
                log("Session ended — shutdown command")
                break

            # ── SPOTIFY COMMAND CHECK ─────────────────────────────────────────
            if handle_spotify_commands(user_input):
                continue  # Handled — don't send to Groq

            # ── GROQ BRAIN ────────────────────────────────────────────────────
            response = think(user_input)
            log(f"SONIC: {response}")

            # ── SPEAK ─────────────────────────────────────────────────────────
            speak(response)


if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        print("\n[SONIC]: Keyboard interrupt received.")
        try:
            pause_music()
        except Exception:
            pass
        speak(f"Emergency shutdown initiated, {USER_TITLE}.")
        log("Session ended — KeyboardInterrupt")
    except Exception as e:
        print(f"\n[SONIC]: Unexpected error: {e}")
        log(f"Session ended — unexpected error: {e}")
    finally:
        print("[SONIC]: Offline.")
