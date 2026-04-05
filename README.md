# S.O.N.I.C. — Systems-Oriented Neural Intelligence Companion



> A fully local, offline-capable personal voice assistant inspired by Iron Man's J.A.R.V.I.S.
> Zero monthly cost. Runs on your machine. Your voice. Your plans. Your music.

---

## What It Does

- **Wakes on voice** — says "Hey Jarvis" (or clap twice) to activate
- **Morning briefing** — greets you by name, reads your daily plan aloud
- **Plays Spotify** — starts your playlist automatically on wake
- **Voice Spotify commands** — "pause music", "next song", "what's playing"
- **Natural conversation** — Groq LLaMA 3.3 70B understands and responds
- **Speaks back** — Kokoro-82M TTS gives it a human voice
- **Starts with Windows** — configured via Task Scheduler

---

## Tech Stack

| Layer | Tool | Cost |
|---|---|---|
| Wake word detection | OpenWakeWord (local) | Free |
| Clap detection | PyAudio energy spike | Free |
| Speech-to-text | OpenAI Whisper (local) | Free |
| LLM brain | Groq API — llama-3.3-70b-versatile | Free tier |
| Text-to-speech | Kokoro-82M (local, GPU) | Free |
| Audio playback | pygame / sounddevice | Free |
| Spotify control | spotipy | Free (Premium needed) |
| Plans file | Local `plans.md` | Free |
| **Total** | | **₹0/month** |

---

## Project Structure

```
sonic/
├── main.py                  # Entry point — full assistant loop
├── wake.py                  # Wake word + clap detection
├── listen.py                # Whisper STT — mic capture + transcription
├── brain.py                 # Groq LLM — conversation + plans injection
├── speak.py                 # Kokoro TTS — text to speech output
├── spotify_control.py       # Spotify playback via spotipy
├── config.py                # All settings in one place
├── train_wake_word.py       # Custom wake word trainer
├── start_sonic.bat          # Windows autostart launcher
├── plans.md                 # Your daily plans (edit this)
├── requirements.txt         # All dependencies
├── .gitignore
├── day1.md                  # Day 1 build log
├── day2.md                  # Day 2 build log
└── logs/
    └── session.log          # Per-session conversation history
```

---

## Setup

### 1. Python Environment

```bash
# Use Python 3.10 or 3.11 — NOT 3.12+
python -m venv venv
venv\Scripts\activate

# Install PyTorch with CUDA (run this FIRST, before requirements.txt)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Install all dependencies
pip install -r requirements.txt
```

### 2. espeak-ng (required for Kokoro TTS)

Download from: https://github.com/espeak-ng/espeak-ng/releases
Install the `.msi` at system level — NOT via pip.

### 3. Download Models

```bash
# Whisper (small model — ~140MB)
python -c "import whisper; whisper.load_model('small')"

# OpenWakeWord hey_jarvis model
python -c "import openwakeword; openwakeword.download_models(['hey_jarvis'])"

# Kokoro auto-downloads on first run (~300MB from HuggingFace)
```

### 4. API Keys

Create a `.env` file (copy from `.env.example` or create manually):

```env
GROQ_API_KEY=your_groq_api_key_here
SPOTIFY_CLIENT_ID=your_spotify_client_id_here
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret_here
SPOTIFY_DEFAULT_PLAYLIST=spotify:playlist:your_playlist_uri_here
```

- **Groq API key**: https://console.groq.com (free tier: 30 req/min, 6000 tokens/min)
- **Spotify credentials**: https://developer.spotify.com (create an app, get Client ID + Secret)
- **Spotify playlist URI**: Right-click any playlist in Spotify → Share → Copy Spotify URI

### 5. Configure plans.md

Edit `plans.md` with your daily schedule. SONIC reads this on wake:

```markdown
## Today's Plan — 2026-04-05
- 9:15 AM: College — Networks lecture
- 3:15 PM: Free — Python roadmap
- 6:00 PM: Gym session
- 8:00 PM: Work on SONIC
```

### 6. First Spotify Auth

```bash
python spotify_control.py
```
This opens a browser for OAuth. After auth, tokens are cached in `.spotify_cache`.

### 7. Run

```bash
python main.py
```

---

## Autostart on Windows

1. Open **Task Scheduler** (`taskschd.msc`)
2. Create Basic Task → Name it "SONIC"
3. Trigger: **At log on**
4. Action: **Start a program**
5. Program: `C:\Users\Rohit\Desktop\sonic\start_sonic.bat`
6. (Optional) Set to run minimised

---

## Voice Commands

| Command | Action |
|---|---|
| "Hey Jarvis" / clap twice | Wake SONIC |
| "Pause music" / "stop music" | Pause Spotify |
| "Play music" / "resume music" | Resume Spotify |
| "Next song" / "skip song" | Skip to next track |
| "What's playing" | Speak current track name |
| "Goodbye Sonic" / "shutdown" | Shutdown and exit |

---

## System Requirements

- **OS**: Windows 10/11
- **Python**: 3.10 or 3.11
- **GPU**: NVIDIA RTX  (CUDA 11.8+)
- **RAM**: 8GB minimum (16GB recommended)
- **Spotify**: Premium account (required for playback control)
- **Groq**: Free API key

---

## Known Notes

1. **Python version is critical** — Kokoro requires Python < 3.13. Use 3.11.
2. **espeak-ng must be system-level** — Kokoro will not work with pip-only install.
3. **Wake phrase** — "Hey Jarvis" is detected by the `hey_jarvis` model. It responds phonetically to "hey sonic" too — reliable for personal use.
4. **Groq free tier** is generous — 6000 tokens/min. SONIC keeps responses short by design.
5. **Ctrl+C** cleanly shuts down and pauses music.

---

## Custom Wake Word (optional)

```bash
python train_wake_word.py
```
Then set `USE_CUSTOM_WAKE = True` in `config.py`.

---

*Built by Rohit Patil*
