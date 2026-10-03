#!/usr/bin/env bash
set -euo pipefail
MIC="plughw:CARD=Device,DEV=0"
SPEAKER="plughw:CARD=MAX98357A,DEV=0"
FILE="/tmp/spyturtle-mic-test.wav"
echo "Detected capture devices:"
arecord -l
echo
echo "Recording 5 seconds from $MIC..."
arecord -q -D "$MIC" -f S16_LE -r 16000 -c1 -d5 "$FILE"
echo "Playing recording through $SPEAKER..."
aplay -q -D "$SPEAKER" "$FILE"
echo "Microphone test complete."
