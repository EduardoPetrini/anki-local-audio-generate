#!/bin/bash
set -euo pipefail

TEXT="${1:-}"
OUTPUT="${2:-}"
VOICE="${3:-ff_siwis}"
SPEED="${4:-1.0}"
SERVER="http://localhost:8080"

if [[ -z "$TEXT" || -z "$OUTPUT" ]]; then
  echo "Usage: $0 \"<text>\" <output-name> [voice] [speed]"
  echo "Example: $0 \"Quelle est la date aujourd'hui?\" output-name ff_siwis 0.8"
  exit 1
fi

curl -sf -X POST "$SERVER/v1/audio/speech" \
  -H "Content-Type: application/json" \
  -d "{\"text\": $(echo "$TEXT" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read().strip()))'), \"voice\": \"$VOICE\", \"speed\": $SPEED}" \
  --output "${OUTPUT}.wav"

echo "Saved: ${OUTPUT}.wav"
