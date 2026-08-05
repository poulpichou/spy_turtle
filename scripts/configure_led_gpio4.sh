#!/usr/bin/env bash
set -euo pipefail

CONFIG=/boot/firmware/config.txt
OVERLAY='dtoverlay=ws2812-pio,gpio=4,num_leds=32,brightness=255'

if [[ ! -f "$CONFIG" ]]; then
    echo "Missing $CONFIG"
    exit 1
fi

BACKUP="${CONFIG}.backup.$(date +%Y%m%d_%H%M%S)"
cp "$CONFIG" "$BACKUP"
echo "Backup created: $BACKUP"

if grep -qE '^[[:space:]]*dtoverlay=ws2812-pio' "$CONFIG"; then
    sed -i -E "s|^[[:space:]]*dtoverlay=ws2812-pio.*$|$OVERLAY|" "$CONFIG"
else
    printf '\n%s\n' "$OVERLAY" >> "$CONFIG"
fi

echo "Configured WS2812B on GPIO4:"
grep -E '^[[:space:]]*dtoverlay=ws2812-pio' "$CONFIG"
echo "Move the LED DATA wire to GPIO4 (physical pin 7), then reboot."
