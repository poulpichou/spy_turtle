#!/bin/bash
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PID_FILE="$ROOT/logs/gpio-server.pid"
if [ -f "$PID_FILE" ]; then
    PID="$(cat "$PID_FILE")"
    if [[ "$PID" =~ ^[0-9]+$ ]] && kill -0 "$PID" 2>/dev/null; then
        CMD="$(tr '\0' ' ' < "/proc/$PID/cmdline" 2>/dev/null || true)"
        if [[ "$CMD" == *robot.gpio_server.server* ]]; then
            kill -TERM "$PID" 2>/dev/null || true
            for i in $(seq 1 30); do
                kill -0 "$PID" 2>/dev/null || break
                sleep 0.1
            done
            if kill -0 "$PID" 2>/dev/null; then echo 'GPIO server did not stop; refusing to force-kill active PWM';exit 1; fi
        fi
    fi
    rm -f "$PID_FILE"
fi
if pgrep -f '[p]ython.*robot.gpio_server.server' >/dev/null; then echo 'GPIO server still running (unknown PID)';exit 1; fi
rm -f /tmp/spyturtle-gpio.sock
echo 'GPIO server stopped'
