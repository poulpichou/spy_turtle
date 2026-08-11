#!/usr/bin/env bash
set -e

echo "=== Caddy service ==="
systemctl is-active caddy

echo
echo "=== spyturtle certificate ==="
echo | openssl s_client -connect spyturtle:443 -servername spyturtle 2>/dev/null \
  | openssl x509 -noout -issuer -dates

echo
echo "=== Intermediate CA ==="
sudo openssl x509 \
  -in /var/lib/caddy/.local/share/caddy/pki/authorities/local/intermediate.crt \
  -noout -issuer -dates

echo
echo "=== Root CA ==="
sudo openssl x509 \
  -in /var/lib/caddy/.local/share/caddy/pki/authorities/local/root.crt \
  -noout -issuer -dates