# Kokoro Local Audio — Configuration

| Key | Default | Description |
| --- | --- | --- |
| `server_url` | `http://localhost:8080` | Base URL of your local Kokoro TTS server. |
| `voice` | `ff_siwis` | Kokoro voice id (e.g. `af_heart`, `ff_siwis`, `am_adam`). |
| `source_field` | `Front` | Fallback field whose text is read and synthesized **when no field is focused**. Normally the audio is generated from the field your cursor is in. Falls back to the first field if the note type has no field with this name. |
| `target_field` | `Front` | Fallback field the `[sound:...]` tag is appended to when no field is focused. When a field is focused, the tag goes into that same field. |
| `timeout_seconds` | `60` | How long to wait for the server before giving up. |
| `shortcut` | `""` | Optional keyboard shortcut for the button, e.g. `"Ctrl+Shift+K"`. Leave empty for none. |
| `play_on_generate` | `true` | Play the audio immediately after it is generated, right inside the Add/Edit window. |
| `speed` | `1.0` | Default playback speed multiplier (`1.0` is normal), pre-selected in the button's speed menu — pick a slower speed there to practise a new language without changing this. The menu offers `0.7×`–`1.3×`: Kokoro slows audio by stretching phoneme durations, so speeds below ~`0.7` start to sound robotic. You can still set any value `0.25`–`4.0` here, and it's added to the menu. |

Tip: click the 🔊 button to choose a speed for that generation (the `speed`
above is the default). The text is taken from whichever field your cursor was
last in, and the `[sound:...]` tag is added back to that same field.

Note: when reading a field, Anki bracket commands such as `[sound:...]`,
`[anki:...]`, and LaTeX (`[latex]`, `[$...$]`) are skipped so they are not
spoken aloud.

After changing values, click **Save**. No restart is required.
