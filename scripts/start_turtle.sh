#!/bin/bash
set -e

cd "$(dirname "$0")/.."

echo "Starting Caddy..."
if ! systemctl is-active --quiet caddy; then
    sudo systemctl start caddy
fi

if ! systemctl is-active --quiet caddy; then
    echo "Caddy failed to start."
    exit 1
fi

if pgrep -f "[r]obot.startup.main" >/dev/null; then
    echo "Spy Turtle is already running."
    exit 1
fi

source .venv/bin/activate

echo "Starting Spy Turtle..."
exec python -m robot.startup.main
