#!/bin/bash
set -e

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
LOG_DIR="$ROOT/logs"
PID_FILE="$LOG_DIR/robot.pid"
LOG_FILE="$LOG_DIR/robot.log"

mkdir -p "$LOG_DIR"

echo "=================================="
echo " Starting Spy Turtle"
echo "=================================="

echo "[1/3] Starting Caddy..."
sudo systemctl start caddy

if ! systemctl is-active --quiet caddy; then
    echo "ERROR: Caddy failed to start."
    exit 1
fi

echo "[2/3] Checking existing process..."

if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if kill -0 "$PID" 2>/dev/null; then
        echo "Spy Turtle already running (PID $PID)."
        exit 0
    fi
    rm -f "$PID_FILE"
fi

if pgrep -f "robot.startup.main" >/dev/null; then
    echo "Spy Turtle already running."
    exit 0
fi

echo "[3/3] Starting robot..."

cd "$ROOT"

nohup "$ROOT/.venv/bin/python" -m robot.startup.main >> "$LOG_FILE" 2>&1 &

PID=$!

echo "$PID" > "$PID_FILE"

sleep 2

if kill -0 "$PID" 2>/dev/null; then
    echo ""
    echo "Spy Turtle started successfully."
    echo ""
    echo "PID    : $PID"
    echo "HTTPS  : https://spyturtle.local"
    echo "Logs   : tail -f $LOG_FILE"
else
    echo "ERROR: startup failed."
    rm -f "$PID_FILE"
    exit 1
fi