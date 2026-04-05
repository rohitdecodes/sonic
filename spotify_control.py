# spotify_control.py
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import time
from config import (
    SPOTIFY_CLIENT_ID,
    SPOTIFY_CLIENT_SECRET,
    SPOTIFY_REDIRECT_URI,
    SPOTIFY_DEFAULT_PLAYLIST,
    SPOTIFY_VOLUME
)

# Spotify OAuth scope — what permissions SONIC needs
SCOPE = "user-read-playback-state user-modify-playback-state user-read-currently-playing"

sp = None  # Spotify client — initialised on first use


def get_spotify_client() -> spotipy.Spotify:
    """
    Returns authenticated Spotify client.
    First call opens browser for OAuth — token cached in .spotify_cache after that.
    """
    global sp
    if sp is None:
        auth_manager = SpotifyOAuth(
            client_id=SPOTIFY_CLIENT_ID,
            client_secret=SPOTIFY_CLIENT_SECRET,
            redirect_uri=SPOTIFY_REDIRECT_URI,
            scope=SCOPE,
            cache_path=".spotify_cache",  # token cached here — never commit to GitHub
            open_browser=True
        )
        sp = spotipy.Spotify(auth_manager=auth_manager)
    return sp


def get_active_device_id() -> str | None:
    """
    Returns the ID of an active Spotify device, or None if none found.
    Tries laptop first, then any other active device.
    """
    try:
        client = get_spotify_client()
        devices = client.devices()

        if not devices or not devices.get("devices"):
            return None

        device_list = devices["devices"]

        # Prefer already-active device
        for device in device_list:
            if device["is_active"]:
                return device["id"]

        # Fall back to first available device
        if device_list:
            return device_list[0]["id"]

        return None

    except Exception as e:
        print(f"[spotify] Device error: {e}")
        return None


def play_music(playlist_uri: str = None) -> bool:
    """
    Start music playback on an active Spotify device.
    If playlist_uri provided, plays that playlist. Otherwise resumes/plays liked songs.
    Returns True if successful, False if no device found or error.
    """
    try:
        client = get_spotify_client()
        device_id = get_active_device_id()

        if not device_id:
            print("[spotify] No active device found. Open Spotify on phone or laptop first.")
            return False

        # Set volume first
        client.volume(SPOTIFY_VOLUME, device_id=device_id)
        time.sleep(0.3)

        if playlist_uri:
            client.start_playback(device_id=device_id, context_uri=playlist_uri)
        else:
            # Play liked songs (saved tracks) if no playlist specified
            client.start_playback(
                device_id=device_id,
                context_uri=SPOTIFY_DEFAULT_PLAYLIST
            )

        print(f"[spotify] Playback started on device: {device_id}")
        return True

    except spotipy.exceptions.SpotifyException as e:
        if "NO_ACTIVE_DEVICE" in str(e) or "404" in str(e):
            print("[spotify] No active device. Open Spotify somewhere first.")
        elif "PREMIUM_REQUIRED" in str(e):
            print("[spotify] Spotify Premium required for API playback control.")
        else:
            print(f"[spotify] Playback error: {e}")
        return False

    except Exception as e:
        print(f"[spotify] Unexpected error: {e}")
        return False


def pause_music() -> bool:
    """Pause current playback."""
    try:
        client = get_spotify_client()
        device_id = get_active_device_id()
        if device_id:
            client.pause_playback(device_id=device_id)
            return True
        return False
    except Exception as e:
        print(f"[spotify] Pause error: {e}")
        return False


def next_track() -> bool:
    """Skip to next track."""
    try:
        client = get_spotify_client()
        device_id = get_active_device_id()
        if device_id:
            client.next_track(device_id=device_id)
            return True
        return False
    except Exception as e:
        print(f"[spotify] Skip error: {e}")
        return False


def get_current_track() -> str:
    """Return currently playing track as 'Artist — Song' string."""
    try:
        client = get_spotify_client()
        current = client.current_playback()
        if current and current.get("item"):
            track = current["item"]
            artist = track["artists"][0]["name"]
            song = track["name"]
            return f"{artist} — {song}"
        return "Nothing playing"
    except Exception as e:
        print(f"[spotify] Track info error: {e}")
        return "Unknown"


if __name__ == "__main__":
    print("Testing Spotify connection...")
    print("First run will open browser for login — log in with your Spotify account.")
    result = play_music()
    if result:
        print("Spotify test PASSED — music should be playing!")
    else:
        print("Spotify test FAILED — check .env keys and make sure Spotify is open.")
