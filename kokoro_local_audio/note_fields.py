"""Helpers for reading from and writing to note fields.

Note fields contain HTML, so the source text is stripped to plain text before
being sent to the TTS server, and the generated ``[sound:...]`` tag is appended
to the target field.
"""

from __future__ import annotations

import hashlib

from anki.notes import Note

import re

try:  # ``strip_html`` location is stable in modern Anki, but guard just in case.
    from anki.utils import strip_html
except Exception:  # pragma: no cover - defensive fallback

    def strip_html(text: str) -> str:
        return re.sub(r"<[^>]+>", " ", text)


# Anki's special field "commands" use square-bracket syntax. We strip them so
# the TTS engine doesn't read out filenames or markup (e.g. an existing
# ``[sound:abc.wav]`` would otherwise be spelled out character by character).
_ANKI_TAG_PATTERNS = (
    re.compile(r"\[sound:[^\]]*\]", re.IGNORECASE),  # [sound:file.mp3]
    re.compile(r"\[/?anki:[^\]]*\]", re.IGNORECASE),  # [anki:tts ...] / [/anki:tts]
    re.compile(r"\[/?latex\]", re.IGNORECASE),  # [latex] / [/latex]
    re.compile(r"\[\$\$?.*?\$\$?\]", re.IGNORECASE | re.DOTALL),  # [$..$] [$$..$$]
)

_WHITESPACE_RE = re.compile(r"\s+")


def strip_anki_tags(text: str) -> str:
    """Remove Anki's square-bracket field commands (sound, tts, latex)."""
    for pattern in _ANKI_TAG_PATTERNS:
        text = pattern.sub(" ", text)
    return text


def _resolve_field(note: Note, preferred: str) -> str:
    """Return ``preferred`` if the note has it, else the note's first field."""
    names = note.keys()
    if preferred in names:
        return preferred
    return names[0]


def read_source_text(note: Note, source_field: str) -> str:
    """Return the speakable plain text of the source field.

    Anki bracket commands (``[sound:...]``, ``[anki:...]``, LaTeX) are removed,
    then HTML is stripped and whitespace collapsed.
    """
    field = _resolve_field(note, source_field)
    text = strip_html(strip_anki_tags(note[field]))
    return _WHITESPACE_RE.sub(" ", text).strip()


def insert_sound_tag(note: Note, target_field: str, filename: str) -> None:
    """Append ``[sound:filename]`` to the target field if not already present."""
    field = _resolve_field(note, target_field)
    tag = f"[sound:{filename}]"
    if tag in note[field]:
        return
    existing = note[field]
    note[field] = f"{existing} {tag}".strip() if existing else tag


def sound_filename(text: str, voice: str) -> str:
    """Build a deterministic, collision-resistant media filename."""
    digest = hashlib.sha1(f"{voice}:{text}".encode("utf-8")).hexdigest()[:12]
    return f"kokoro-{voice}-{digest}.wav"
