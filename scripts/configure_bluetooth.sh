#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/.."
echo "[Bluetooth] Installing BLE server dependency..."
python -m pip install "bless==0.3.0"
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
