# Changelog

All notable changes to **Kokoro Local Audio** are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
[Unreleased]: <REPO_URL>/compare/v1.1.0...HEAD
[1.1.0]: <REPO_URL>/compare/v1.0.0...v1.1.0
[1.0.0]: <REPO_URL>/releases/tag/v1.0.0
