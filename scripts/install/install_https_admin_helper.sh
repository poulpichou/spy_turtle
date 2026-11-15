#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
sudo install -o root -g root -m 0755 "$ROOT/scripts/install/spyturtle-add-https-ip" /usr/local/sbin/spyturtle-add-https-ip
# Restrict privilege escalation to this one root-owned, argument-free helper.
USER_NAME="$(id -un)"
case "$USER_NAME" in *[!a-zA-Z0-9_-]*|'') echo "Invalid username"; exit 1;; esac
RULE="$USER_NAME ALL=(root) NOPASSWD: /usr/local/sbin/spyturtle-add-https-ip"
printf '%s\n' "$RULE" | sudo tee /etc/sudoers.d/spyturtle-https-admin >/dev/null
sudo chmod 0440 /etc/sudoers.d/spyturtle-https-admin
sudo visudo -cf /etc/sudoers.d/spyturtle-https-admin
printf 'HTTPS admin helper installed for %s\n' "$USER_NAME"
