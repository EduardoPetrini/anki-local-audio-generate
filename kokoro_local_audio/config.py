"""Typed access to the add-on configuration.

Anki stores add-on config as JSON (see ``config.json``) and lets the user edit
it from *Tools → Add-ons → Config*. This module reads that config and exposes
it as an immutable value object so the rest of the code never touches raw
dicts or worries about missing keys.
"""

from __future__ import annotations

from dataclasses import dataclass

from aqt import mw

# Fallbacks used when a key is missing from the user's config. These mirror the
# defaults shipped in ``config.json``.
_DEFAULTS = {
    "server_url": "http://localhost:8080",
    "voice": "ff_siwis",
    "source_field": "Front",
    "target_field": "Front",
    "timeout_seconds": 60,
    "shortcut": "",
    "play_on_generate": True,
    "speed": 1.0,
}

# Kokoro accepts a playback speed multiplier in this range (OpenAI-compatible
# ``speed`` parameter). Values outside it are clamped before each request.
SPEED_MIN = 0.25
SPEED_MAX = 4.0


@dataclass(frozen=True)
class Config:
    """Immutable snapshot of the add-on settings."""

    server_url: str
    voice: str
    source_field: str
    target_field: str
    timeout_seconds: int
    shortcut: str
    play_on_generate: bool
    speed: float


def clamp_speed(speed: float) -> float:
    """Constrain a speed multiplier to the range Kokoro accepts."""
    return max(SPEED_MIN, min(SPEED_MAX, speed))


def get_config() -> Config:
    """Read the current add-on config, falling back to defaults per key."""
    raw = mw.addonManager.getConfig(__name__) or {}

    def value(key: str):
        got = raw.get(key)
        return got if got not in (None, "") else _DEFAULTS[key]

    return Config(
        server_url=str(value("server_url")).rstrip("/"),
        voice=str(value("voice")),
        source_field=str(value("source_field")),
        target_field=str(value("target_field")),
        timeout_seconds=int(value("timeout_seconds")),
        shortcut=str(raw.get("shortcut") or ""),
        play_on_generate=bool(raw.get("play_on_generate", _DEFAULTS["play_on_generate"])),
        speed=clamp_speed(_coerce_speed(value("speed"))),
    )


def _coerce_speed(raw_speed) -> float:
    """Read a speed value, falling back to the default if it isn't a number."""
    try:
        return float(raw_speed)
    except (TypeError, ValueError):
        return float(_DEFAULTS["speed"])
