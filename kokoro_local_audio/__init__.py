"""Kokoro Local Audio — Anki add-on.

Adds a toolbar button to the note editor that turns the text in the source
field into speech using a locally running Kokoro TTS server, then inserts the
resulting ``[sound:...]`` tag into the target field.

The add-on never talks to the network: it only calls the Kokoro server the
user runs on their own machine (default ``http://localhost:8080``). If that
server is not reachable, the user is told how to install/start it.
"""

from __future__ import annotations

from aqt import gui_hooks
from aqt.editor import Editor
from aqt.operations import QueryOp
from aqt.sound import av_player
from aqt.utils import showWarning, tooltip

from .config import get_config
from .kokoro import KokoroError, KokoroUnavailable, synthesize
from .note_fields import insert_sound_tag, read_source_text, sound_filename

BUTTON_CMD = "kokoro_generate_audio"
BUTTON_LABEL = "🔊"
BUTTON_TIP = "Generate audio from the front field (Kokoro TTS)"


def _on_generate(editor: Editor) -> None:
    """Editor button handler: synthesize audio for the current note."""
    note = editor.note
    if note is None:
        tooltip("No note is currently open.")
        return

    cfg = get_config()
    text = read_source_text(note, cfg.source_field)
    if not text:
        tooltip("The source field is empty — nothing to synthesize.")
        return

    def op(col) -> str:
        audio = synthesize(text, cfg)
        # ``write_data`` may rename to avoid collisions; trust its return value.
        return col.media.write_data(sound_filename(text, cfg.voice), audio)

    def on_success(filename: str) -> None:
        # ``editor.note`` can change while the request is in flight; re-read it.
        current = editor.note
        if current is None:
            return
        insert_sound_tag(current, cfg.target_field, filename)
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
        func=_on_generate,
        tip=BUTTON_TIP,
        label=BUTTON_LABEL,
        keys=get_config().shortcut or None,
    )
    buttons.append(button)


gui_hooks.editor_did_init_buttons.append(_add_editor_button)
