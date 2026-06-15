"""Client for a locally running Kokoro TTS server.

Mirrors ``generate.sh``: POST ``{"text": ..., "voice": ...}`` to
``/v1/audio/speech`` and read back WAV audio bytes. Uses only the Python
standard library so the add-on has zero third-party dependencies.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .config import Config

SPEECH_ENDPOINT = "/v1/audio/speech"


class KokoroError(Exception):
    """A Kokoro request failed for a reason we can explain to the user."""


class KokoroUnavailable(KokoroError):
    """The Kokoro server could not be reached at all."""


def _not_running_message(server_url: str, detail: str) -> str:
    return (
        f"Could not reach a Kokoro TTS server at {server_url}.\n\n"
        f"Details: {detail}\n\n"
        "Make sure Kokoro is installed and running locally, then try again.\n"
        "Install/run Kokoro: https://github.com/remsky/Kokoro-FastAPI\n\n"
        "You can change the server URL in Tools → Add-ons → "
        "Kokoro Local Audio → Config."
    )


def synthesize(text: str, cfg: "Config") -> bytes:
    """Synthesize ``text`` to WAV audio bytes using the Kokoro server.

    Raises:
        KokoroUnavailable: the server is not reachable (e.g. not running).
        KokoroError: the server responded with an error status or no audio.
    """
    url = cfg.server_url + SPEECH_ENDPOINT
    payload = json.dumps({"text": text, "voice": cfg.voice}).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=cfg.timeout_seconds) as response:
            audio = response.read()
    except urllib.error.HTTPError as exc:
        body = _safe_body(exc)
        raise KokoroError(
            f"Kokoro returned an error ({exc.code} {exc.reason}) for voice "
            f"'{cfg.voice}'.\n\n{body}".strip()
        ) from exc
    except urllib.error.URLError as exc:
        raise KokoroUnavailable(
            _not_running_message(cfg.server_url, str(exc.reason))
        ) from exc
    except (TimeoutError, OSError) as exc:
        raise KokoroUnavailable(
            _not_running_message(cfg.server_url, str(exc))
        ) from exc

    if not audio:
        raise KokoroError("Kokoro returned an empty audio response.")
    return audio


def _safe_body(exc: urllib.error.HTTPError) -> str:
    try:
        return exc.read().decode("utf-8", errors="replace")[:500]
    except Exception:
        return ""
