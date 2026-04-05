# config.py
import os
from dotenv import load_dotenv

load_dotenv()

# --- API Keys ---
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "your_groq_key_here")

# --- Spotify ---
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID", "your_spotify_client_id")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET", "your_spotify_secret")
SPOTIFY_REDIRECT_URI = "http://127.0.0.1:8888/callback"

# Your default playlist URI — get this from Spotify:
# Open Spotify → right-click any playlist → Share → Copy Spotify URI
# Looks like: spotify:playlist:37i9dQZF1DXcBWIGoYBM5M
# Use your own liked songs playlist or any playlist URI you want
SPOTIFY_DEFAULT_PLAYLIST = os.getenv(
    "SPOTIFY_DEFAULT_PLAYLIST",
    "spotify:playlist:37i9dQZF1DXcBWIGoYBM5M"  # Spotify's "Today's Top Hits" as fallback
)
SPOTIFY_VOLUME = 40  # 0-100 — 40 is good for background music while working

# --- SONIC Identity ---
ASSISTANT_NAME = "Sonic"
USER_NAME = "Rohit"
USER_TITLE = "Sir"

# --- Whisper ---
WHISPER_MODEL = "small"

# --- Kokoro ---
KOKORO_VOICE = "am_michael"
KOKORO_SPEED = 1.0

# --- Groq ---
GROQ_MODEL = "llama-3.3-70b-versatile"
MAX_TOKENS = 300

# --- OpenWakeWord ---
WAKE_MODEL = "hey_jarvis"
WAKE_THRESHOLD = 0.5
USE_CUSTOM_WAKE = False          # Set True after running train_wake_word.py
CUSTOM_WAKE_PATH = "models/hey_sonic_custom.joblib"

# --- Behavior ---
SILENCE_TIMEOUT = 300
PLANS_FILE = "plans.md"
LOG_FILE = "logs/session.log"
