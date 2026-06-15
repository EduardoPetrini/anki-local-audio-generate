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
}


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
    )
