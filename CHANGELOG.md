# Changelog

All notable changes to **Kokoro Local Audio** are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.2.0] — 2026-06-15

### Added
- **Choose the audio speed.** Clicking the 🔊 button now opens a menu of
  playback speeds (0.7×–1.3×) so you can slow audio down for language practice
  without opening settings. A new `speed` config option (default `1.0`) sets the
  pre-selected default; Kokoro accepts `0.25`–`4.0` and values are clamped. The
  menu stays at 0.7× and above because Kokoro slows speech by stretching phoneme
  durations, which sounds robotic at lower speeds — set a more extreme `speed` in
  the config if you want it offered anyway.

### Changed
- **Audio follows the cursor.** Text is now read from whichever field you last
  focused, and the `[sound:...]` tag is added back to that same field — so
  generating from the Back field reads and tags the Back text. When no field is
  focused, the configured `source_field`/`target_field` are used as before.
- Generated filenames now include the speed, so the same text at different
  speeds produces distinct media files instead of overwriting each other.

## [1.1.0] — 2026-06-12

### Added
- Audio now plays immediately after it is generated, right inside the Add/Edit
  window — no need to close the editor first. New `play_on_generate` config
  option (default `true`) to disable this.

### Changed
- The source field's Anki bracket commands are now skipped before synthesis, so
  an existing `[sound:...]` tag (or `[anki:...]` / LaTeX markup) is no longer
  read out character by character. Whitespace is also collapsed for cleaner
  speech input.

## [1.0.0] — 2026-06-12

### Added
- 🔊 editor toolbar button that synthesizes the source field's text into speech
  via a locally running Kokoro TTS server (`POST /v1/audio/speech`).
- Background synthesis using `QueryOp` so the UI never freezes.
- Generated WAV is written to the collection media and a `[sound:...]` tag is
  appended to the target field.
- Friendly, actionable errors that distinguish "Kokoro not running"
  (`KokoroUnavailable`) from a server-side error (`KokoroError`).
- User-editable config: `server_url`, `voice`, `source_field`, `target_field`,
  `timeout_seconds`, and an optional keyboard `shortcut`.
- Stdlib-only implementation — no third-party dependencies.

<!-- Replace <REPO_URL> with this add-on's repository once it is published. -->
[Unreleased]: <REPO_URL>/compare/v1.2.0...HEAD
[1.2.0]: <REPO_URL>/compare/v1.1.0...v1.2.0
[1.1.0]: <REPO_URL>/compare/v1.0.0...v1.1.0
[1.0.0]: <REPO_URL>/releases/tag/v1.0.0
