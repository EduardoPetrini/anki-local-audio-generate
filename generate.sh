#!/bin/bash
set -euo pipefail

TEXT="${1:-}"
OUTPUT="${2:-}"
VOICE="${3:-ff_siwis}"
SERVER="http://localhost:8080"

if [[ -z "$TEXT" || -z "$OUTPUT" ]]; then
  echo "Usage: $0 \"<text>\" <output-name> [voice]"
  echo "Example: $0 \"Quelle est la date aujourd'hui?\" output-name"
  exit 1
fi

curl -sf -X POST "$SERVER/v1/audio/speech" \
  -H "Content-Type: application/json" \
  -d "{\"text\": $(echo "$TEXT" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read().strip()))'), \"voice\": \"$VOICE\"}" \
  --output "${OUTPUT}.wav"

echo "Saved: ${OUTPUT}.wav"
