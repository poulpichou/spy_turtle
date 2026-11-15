#!/bin/bash
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
mkdir -p logs
PID_FILE="$ROOT/logs/gpio-server.pid"
SOCKET=/tmp/spyturtle-gpio.sock
if [ -f "$PID_FILE" ] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then echo "GPIO server already running"; exit 0; fi
if pgrep -f '[p]ython.*robot.gpio_server.server' >/dev/null; then echo 'GPIO server already running without PID file'; exit 1; fi
rm -f "$PID_FILE"
if [ ! -x "$ROOT/.venv/bin/python" ]; then echo 'Missing Python venv'; exit 1; fi
# Dedicated GPIO log; rotate at every full start, preserve last 3 sessions.
for n in 3 2 1; do
    if [ "$n" = 3 ]; then rm -f logs/gpio-server.log.3; else mv -f "logs/gpio-server.log.$n" "logs/gpio-server.log.$((n+1))" 2>/dev/null || true; fi
done
[ ! -f logs/gpio-server.log ] || mv -f logs/gpio-server.log logs/gpio-server.log.1
printf '\n==== GPIO server startup %s ====\n' "$(date -Is)" >> logs/gpio-server.log
nohup "$ROOT/.venv/bin/python" -u -m robot.gpio_server.server >> logs/gpio-server.log 2>&1 &
PID=$!
echo "$PID" > "$PID_FILE"
for i in $(seq 1 40); do
    if [ -S "$SOCKET" ] && "$ROOT/.venv/bin/python" -c 'from robot.gpio_server.client import client;client.call("motors","status")' >/dev/null 2>&1; then
        echo "GPIO server ready PID=$PID log=logs/gpio-server.log";exit 0
    fi
    if ! kill -0 "$PID" 2>/dev/null; then break; fi
    sleep 0.25
done
echo 'GPIO server failed to become ready';tail -40 logs/gpio-server.log;exit 1
