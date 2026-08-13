#!/usr/bin/env bash
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PYTHON="$ROOT/.venv/bin/python"
if [ ! -x "$PYTHON" ]; then echo "Missing virtualenv Python: $PYTHON"; exit 1; fi
echo "[Bluetooth] Installing BLE server dependency in project virtualenv..."
"$PYTHON" -m pip install "bless==0.3.0"
echo "[Bluetooth] Enabling BlueZ..."
sudo systemctl enable --now bluetooth
sudo rfkill unblock bluetooth 2>/dev/null || true
bluetoothctl power on
echo
echo "[Bluetooth] Controller:"
bluetoothctl show | grep -E "Controller|Name:|Powered:|Discoverable:|Pairable:" || true
echo
echo "Done. Restart Spy Turtle, then check:"
echo "  tail -f ~/spy_turtle/logs/log | grep BLUETOOTH"
