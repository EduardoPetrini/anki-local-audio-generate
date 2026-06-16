"""Kokoro Local Audio — Anki add-on.

Adds a toolbar button to the note editor that turns field text into speech
using a locally running Kokoro TTS server, then inserts the resulting
``[sound:...]`` tag back into that field.

Clicking the button opens a small menu of playback speeds so the user can slow
the audio down (handy when learning a new language) without opening settings;
the configured ``speed`` is the pre-selected default. The text is read from
whichever field the cursor was last in, so generating from the Back field reads
the Back text. When no field is focused it falls back to the configured
``source_field``/``target_field``.

The add-on never talks to the network: it only calls the Kokoro server the
user runs on their own machine (default ``http://localhost:8080``). If that
server is not reachable, the user is told how to install/start it.
"""

from __future__ import annotations

from aqt import gui_hooks
from aqt.editor import Editor
from aqt.operations import QueryOp
from aqt.qt import QCursor, QMenu
from aqt.sound import av_player
from aqt.utils import showWarning, tooltip

from .config import get_config
from .kokoro import KokoroError, KokoroUnavailable, synthesize
from .note_fields import (
    active_field_name,
    insert_sound_tag,
    read_source_text,
    sound_filename,
)

BUTTON_CMD = "kokoro_generate_audio"
BUTTON_LABEL = "🔊"
BUTTON_TIP = "Generate audio from the active field (Kokoro TTS) — pick a speed"

# Speeds offered in the button menu. Kokoro implements speed by scaling the
# model's predicted phoneme durations (``duration / speed``), not by stretching
# the waveform, so values far from 1.0 push durations out of the model's trained
# range and sound robotic. We keep the floor at 0.7×, where speech still sounds
# natural. The configured ``speed`` is merged in (see ``_show_speed_menu``), so a
# user who deliberately sets a more extreme value can still select it.
SPEED_CHOICES = (0.7, 0.85, 1.0, 1.15, 1.3)


def _show_speed_menu(editor: Editor) -> None:
    """Editor button handler: let the user pick a speed, then synthesize."""
    if editor.note is None:
        tooltip("No note is currently open.")
        return

    cfg = get_config()
    menu = QMenu(editor.widget)
    speeds = sorted({*SPEED_CHOICES, round(cfg.speed, 3)})
    for speed in speeds:
        is_default = abs(speed - cfg.speed) < 1e-9
        label = f"{speed:g}×  (default)" if is_default else f"{speed:g}×"
        action = menu.addAction(label)
        # Bind ``speed`` per-iteration so each action keeps its own value.
        action.triggered.connect(
            lambda _checked=False, chosen=speed: _generate(editor, chosen)
        )
    menu.exec(QCursor.pos())


def _generate(editor: Editor, speed: float) -> None:
    """Synthesize the active field's text at ``speed`` and insert the tag."""
    note = editor.note
    if note is None:
        tooltip("No note is currently open.")
        return

    cfg = get_config()
    # ``currentField`` is cleared when the button click blurs the field, so use
    # ``last_field_index`` (retained across blur) to find the active field.
    active = active_field_name(note, getattr(editor, "last_field_index", None))
    source_field = active if active is not None else cfg.source_field
    target_field = active if active is not None else cfg.target_field

    text = read_source_text(note, source_field)
    if not text:
        tooltip("The active field is empty — nothing to synthesize.")
        return

    def op(col) -> str:
        audio = synthesize(text, cfg, speed)
        # ``write_data`` may rename to avoid collisions; trust its return value.
        return col.media.write_data(sound_filename(text, cfg.voice, speed), audio)

    def on_success(filename: str) -> None:
        # ``editor.note`` can change while the request is in flight; re-read it.
        current = editor.note
        if current is None:
            return
        insert_sound_tag(current, target_field, filename)
        editor.loadNote()
        tooltip(f"Audio added: [sound:{filename}]")
        if cfg.play_on_generate:
            # ``filename`` is a bare media name; av_player resolves it against
            # the collection's media folder and plays it right away.
            av_player.play_file(filename)

    (
        QueryOp(parent=editor.parentWindow, op=op, success=on_success)
        .with_progress("Generating audio with Kokoro…")
        .failure(_on_failure)
        .run_in_background()
    )


def _on_failure(exc: Exception) -> None:
    """Show a friendly, actionable error instead of a raw traceback."""
    if isinstance(exc, (KokoroUnavailable, KokoroError)):
        showWarning(str(exc), title="Kokoro Local Audio")
        return
    showWarning(
        f"Unexpected error while generating audio:\n\n{exc}",
        title="Kokoro Local Audio",
    )


def _add_editor_button(buttons: list[str], editor: Editor) -> None:
    button = editor.addButton(
        icon=None,
        cmd=BUTTON_CMD,
        func=_show_speed_menu,
        tip=BUTTON_TIP,
        label=BUTTON_LABEL,
        keys=get_config().shortcut or None,
    )
    buttons.append(button)


gui_hooks.editor_did_init_buttons.append(_add_editor_button)
