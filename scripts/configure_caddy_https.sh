#!/usr/bin/env bash
set -euo pipefail
SOURCE="$(cd "$(dirname "$0")/.." && pwd)/deploy/caddy/Caddyfile"
TARGET="/etc/caddy/Caddyfile"
BACKUP="/etc/caddy/Caddyfile.backup.$(date +%Y%m%d_%H%M%S)"

if [[ ! -f "$SOURCE" ]]; then echo "Missing $SOURCE"; exit 1; fi
echo "Backing up $TARGET -> $BACKUP"
sudo cp "$TARGET" "$BACKUP"
sudo cp "$SOURCE" "$TARGET"

if ! sudo caddy validate --config "$TARGET" --adapter caddyfile; then
    echo "Caddy validation failed, restoring backup"
    sudo cp "$BACKUP" "$TARGET"
    exit 1
fi

sudo systemctl restart caddy
sleep 2
if ! sudo systemctl is-active --quiet caddy; then
    echo "Caddy failed to start, restoring backup"
    sudo cp "$BACKUP" "$TARGET"
    sudo systemctl restart caddy
    sudo journalctl -u caddy -n 60 --no-pager
    exit 1
fi

echo
echo "Caddy is active."
echo "Configured internal certificate lifetime: 90 days"
echo "Configured intermediate lifetime: 1825 days (5 years)"
echo
echo "Certificate currently served:"
echo | openssl s_client -connect spyturtle:443 -servername spyturtle 2>/dev/null | openssl x509 -noout -subject -issuer -dates || true
echo
echo "If the phone still shows the previous certificate, fully close the PWA/Chrome tab and reopen it."
