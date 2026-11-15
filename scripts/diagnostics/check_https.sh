#!/usr/bin/env bash
set -u
echo "[HTTPS] caddy=$(systemctl is-active caddy 2>/dev/null||true)"
if ss -ltn|grep -qE '[:.]443[[:space:]]';then echo "[HTTPS] port 443=listening";else echo "[HTTPS] port 443=closed";fi
CODE="$(curl -k -sS -o /dev/null -w '%{http_code}' --max-time 5 https://127.0.0.1/health -H 'Host: spyturtle.local'||true)"
echo "[HTTPS] proxy=${CODE:-failed}"
