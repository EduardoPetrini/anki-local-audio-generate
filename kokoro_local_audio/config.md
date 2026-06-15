# Kokoro Local Audio — Configuration

| Key | Default | Description |
| --- | --- | --- |
| `server_url` | `http://localhost:8080` | Base URL of your local Kokoro TTS server. |
| `voice` | `ff_siwis` | Kokoro voice id (e.g. `af_heart`, `ff_siwis`, `am_adam`). |
| `source_field` | `Front` | Field whose text is read and synthesized. Falls back to the first field if the note type has no field with this name. |
| `target_field` | `Front` | Field the `[sound:...]` tag is appended to. Falls back to the first field. |
| `timeout_seconds` | `60` | How long to wait for the server before giving up. |
| `shortcut` | `""` | Optional keyboard shortcut for the button, e.g. `"Ctrl+Shift+K"`. Leave empty for none. |
| `play_on_generate` | `true` | Play the audio immediately after it is generated, right inside the Add/Edit window. |

Note: when reading the source field, Anki bracket commands such as
`[sound:...]`, `[anki:...]`, and LaTeX (`[latex]`, `[$...$]`) are skipped so
they are not spoken aloud.

After changing values, click **Save**. No restart is required.
