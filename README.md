# Kokoro Local Audio — Anki Add-on

Add a **🔊 button** to the Anki note editor that turns the text in the field
you're editing into speech using a **Kokoro TTS server running locally on your
own machine**. Pick a playback speed from the button's menu (slow it down for
language practice), and the generated audio is saved into your collection's
media with a `[sound:...]` tag inserted into the card, so it plays during
review like any other Anki audio.

No cloud services, no API keys, no telemetry — the add-on only talks to the
Kokoro server you run yourself (default `http://localhost:8080`).

---

## How it works

1. You open the **Add** (or **Edit**) note window, click into the field you want
   audio for, then click the **🔊** button and pick a **speed** from its menu
   (the configured `speed` is the default).
2. The add-on reads the text from the **field you last focused** (e.g. `Back` if
   that's where your cursor was), strips the HTML, and POSTs it to your local
   Kokoro server's `/v1/audio/speech` endpoint — exactly like the bundled
   [`generate.sh`](generate.sh).
3. The returned WAV audio is written into Anki's media folder with a stable,
   collision-resistant filename (the speed is part of it, so the same text at
   different speeds doesn't collide).
4. A `[sound:<file>.wav]` tag is appended to that **same field**. If no field is
   focused, the configured `source_field`/`target_field` (default `Front`) are
   used instead.

If the Kokoro server is not reachable, you get a clear message explaining that
Kokoro is not running and where to install it — nothing is written to your note.

---

## Requirements

- **Anki 2.1.50+** (Qt6 builds; the add-on uses the modern `gui_hooks` /
  `QueryOp` APIs).
- A **local Kokoro TTS server** exposing the OpenAI-style
  `POST /v1/audio/speech` endpoint. The reference server is
  [**Kokoro-FastAPI**](https://github.com/remsky/Kokoro-FastAPI).

### Installing & running Kokoro

Follow the [Kokoro-FastAPI](https://github.com/remsky/Kokoro-FastAPI) README.
A common quick start is via Docker:

```bash
docker run -p 8080:8880 ghcr.io/remsky/kokoro-fastapi-cpu
```

> Map whichever container port your image exposes to host port **8080** (or set
> a different `server_url` in the add-on config). Verify it's up:
>
> ```bash
> curl -sf -X POST http://localhost:8080/v1/audio/speech \
>   -H "Content-Type: application/json" \
>   -d '{"text":"Bonjour le monde","voice":"ff_siwis"}' --output test.wav
> ```

You should get a playable `test.wav`. If this works, the add-on will work.

---

## Installing the add-on

### Option A — Manual install (recommended for local use)

Copy the `kokoro_local_audio/` folder into your Anki add-ons directory and
restart Anki.

| OS | Add-ons folder |
| --- | --- |
| macOS | `~/Library/Application Support/Anki2/addons21/` |
| Windows | `%APPDATA%\Anki2\addons21\` |
| Linux | `~/.local/share/Anki2/addons21/` |

```bash
# macOS example
cp -R kokoro_local_audio "$HOME/Library/Application Support/Anki2/addons21/"
```

Then restart Anki. You should see a **🔊** button in the editor toolbar when
adding or editing a note.

### Option B — Install the packaged `.ankiaddon`

Build a distributable package and install it through Anki's UI:

```bash
cd kokoro_local_audio
zip -r ../kokoro_local_audio.ankiaddon . -x '__pycache__/*'
```

In Anki: **Tools → Add-ons → Install from file…** and select
`kokoro_local_audio.ankiaddon`, then restart.

---

## Usage

1. Start your local Kokoro server.
2. In Anki, open **Add** (or edit an existing note).
3. Click into the field you want audio for (e.g. **Front** or **Back**) and type
   your text.
4. Click the **🔊** button and choose a **speed** from the menu (e.g. `0.7×` to
   slow it down for a new language).
5. A short progress dialog appears; when it finishes, the `[sound:...]` tag is
   added to that field and a tooltip confirms it. Play it back with the standard
   Anki audio controls or during review.

---

## Configuration

Open **Tools → Add-ons → Kokoro Local Audio → Config**.

| Key | Default | Description |
| --- | --- | --- |
| `server_url` | `http://localhost:8080` | Base URL of your local Kokoro server. |
| `voice` | `ff_siwis` | Kokoro voice id (e.g. `af_heart`, `am_adam`, `ff_siwis`). |
| `source_field` | `Front` | Fallback field synthesized **only when no field is focused**. Normally the focused field is used. Falls back to the note's first field if absent. |
| `target_field` | `Front` | Fallback field the `[sound:...]` tag is appended to when no field is focused; otherwise the focused field is used. |
| `timeout_seconds` | `60` | How long to wait for the server before giving up. |
| `shortcut` | `""` | Optional keyboard shortcut, e.g. `Ctrl+Shift+K`. Empty = none. |
| `speed` | `1.0` | Default playback speed, pre-selected in the 🔊 button's speed menu. The menu offers `0.7×`–`1.3×`, where speech still sounds natural; Kokoro slows audio by stretching phoneme durations, so lower values sound robotic. Set any value `0.25`–`4.0` here and it's added to the menu too. |

Changes take effect immediately after saving — no restart needed.

---

## Troubleshooting

**"Could not reach a Kokoro TTS server…"**
The server isn't running or isn't listening on the configured URL. Start Kokoro
and confirm the `curl` test above works, then check `server_url` in the config.

**"Kokoro returned an error (404 / 422 …)"**
The server is reachable but rejected the request — usually an unknown `voice`.
Pick a voice your Kokoro build supports and update the config.

**The 🔊 button doesn't appear.**
Ensure you're on Anki 2.1.50+ (Qt6) and that the add-on is enabled under
**Tools → Add-ons**. Check **Tools → Add-ons → View Files** to confirm the
`kokoro_local_audio` folder is present, and look at Anki's error console for
load errors.

**Audio added but doesn't play.**
Confirm the `[sound:...]` tag is present in the field and that the file exists
in your media folder (**Tools → Check Media**).

---

## Project layout

```
anki-plugin-local-audio/
├── generate.sh                  # Reference shell script the add-on mirrors
├── README.md                    # This file
└── kokoro_local_audio/          # The installable add-on
    ├── __init__.py              # Registers the editor button + orchestration
    ├── config.py                # Typed, immutable config access
    ├── config.json              # Default config (editable in Anki)
    ├── config.md                # Config help shown in Anki
    ├── kokoro.py                # Stdlib-only Kokoro HTTP client
    ├── note_fields.py           # Field read/write + media filename helpers
    └── manifest.json            # Add-on metadata
```

The add-on uses **only the Python standard library** plus Anki's own APIs — no
extra dependencies to install.

---

## Privacy

All speech synthesis happens on your machine against a server you control. The
add-on makes no other network requests.
