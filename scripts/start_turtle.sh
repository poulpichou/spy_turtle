#!/bin/bash
set -e

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
LOG_DIR="$ROOT/logs"
PID_FILE="$LOG_DIR/robot.pid"
LOG_FILE="$LOG_DIR/turtle.log.1"
LOG_LINK="$LOG_DIR/log"

cd "$ROOT"
mkdir -p "$LOG_DIR"

echo "Starting HTTPS proxy..."
LOCAL_IP="$(hostname -I | awk '{print $1}')"
if [ -z "$LOCAL_IP" ]; then echo "Cannot determine LAN IPv4 address"; exit 1; fi
echo "Local HTTPS bind: $LOCAL_IP"
printf 'SPY_LOCAL_IP=%s\n' "$LOCAL_IP" | sudo tee /etc/default/spy-turtle-caddy >/dev/null
sudo mkdir -p /etc/systemd/system/caddy.service.d
printf '[Service]\nEnvironmentFile=/etc/default/spy-turtle-caddy\n' | sudo tee /etc/systemd/system/caddy.service.d/spy-turtle.conf >/dev/null
sudo systemctl daemon-reload
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

echo "Rotating logs..."
rm -f "$LOG_DIR/turtle.log.3"

if [ -f "$LOG_DIR/turtle.log.2" ]; then
    mv "$LOG_DIR/turtle.log.2" "$LOG_DIR/turtle.log.3"
fi

if [ -f "$LOG_DIR/turtle.log.1" ]; then
    mv "$LOG_DIR/turtle.log.1" "$LOG_DIR/turtle.log.2"
fi

touch "$LOG_FILE"
ln -sfn "turtle.log.1" "$LOG_LINK"

{
    echo "============================================================"
    echo "Spy Turtle startup"
    echo "Date: $(date '+%Y-%m-%d %H:%M:%S %Z')"
    echo "Host: $(hostname)"
    echo "Kernel: $(uname -r)"
    echo "============================================================"
} >> "$LOG_FILE"

# The GPIO child owns motor/servo pins; launch it before the main process.
if "$ROOT/.venv/bin/python" -c 'from robot.config import settings;raise SystemExit(not (settings.GPIO_SERVER_ENABLED and not settings.SIMULATION))'; then
    echo 'Starting isolated GPIO server...'
    bash "$ROOT/scripts/gpio_server/start_gpio.sh"
fi

echo "Starting Spy Turtle..."
nohup "$ROOT/.venv/bin/python" -u -m robot.startup.main >> "$LOG_FILE" 2>&1 &
PID=$!
echo "$PID" > "$PID_FILE"

sleep 2

if kill -0 "$PID" 2>/dev/null; then
    echo "Spy Turtle started with PID $PID."
    echo "HTTPS: https://spyturtle.local"
    echo "Current log: tail -f $LOG_LINK"
    echo "Previous log: tail -100 $LOG_DIR/turtle.log.2"
else
    echo "Spy Turtle failed to start."
    rm -f "$PID_FILE"
    tail -50 "$LOG_FILE" 2>/dev/null || true
    exit 1
fi