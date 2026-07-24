#!/bin/bash
set -e

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
LOG_DIR="$ROOT/logs"
PID_FILE="$LOG_DIR/robot.pid"
LOG_FILE="$LOG_DIR/robot.log"

cd "$ROOT"
mkdir -p "$LOG_DIR"

echo "Starting HTTPS proxy..."
sudo systemctl restart caddy

if ! systemctl is-active --quiet caddy; then
    echo "Caddy failed to start."
    sudo systemctl status caddy --no-pager
    exit 1
fi

if [ -f "$PID_FILE" ]; then
    PID="$(cat "$PID_FILE")"
    if kill -0 "$PID" 2>/dev/null; then
        echo "Spy Turtle is already running with PID $PID."
        exit 0
    fi
    rm -f "$PID_FILE"
fi

if pgrep -f "[r]obot.startup.main" >/dev/null; then
    echo "Spy Turtle is already running."
    exit 0
fi

if [ ! -x "$ROOT/.venv/bin/python" ]; then
    echo "Python virtual environment not found: $ROOT/.venv"
    exit 1
fi

echo "Starting Spy Turtle..."
nohup "$ROOT/.venv/bin/python" -m robot.startup.main >> "$LOG_FILE" 2>&1 &
PID=$!
echo "$PID" > "$PID_FILE"

sleep 2

if kill -0 "$PID" 2>/dev/null; then
    echo "Spy Turtle started with PID $PID."
    echo "HTTPS: https://spyturtle.local"
    echo "Logs: tail -f $LOG_FILE"
else
    echo "Spy Turtle failed to start."
    rm -f "$PID_FILE"
    tail -50 "$LOG_FILE" 2>/dev/null || true
    exit 1
fi