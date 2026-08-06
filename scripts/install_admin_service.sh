#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
USER_NAME="${SUDO_USER:-$USER}"

sudo tee /etc/systemd/system/spy-turtle.service >/dev/null <<EOF
[Unit]
Description=Spy Turtle
After=network-online.target
Wants=network-online.target

[Service]
Type=forking
User=$USER_NAME
WorkingDirectory=$ROOT
ExecStart=$ROOT/scripts/start_turtle.sh
ExecStop=$ROOT/scripts/stop_turtle.sh
PIDFile=$ROOT/logs/robot.pid
Restart=on-failure
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

sudo tee /etc/sudoers.d/spy-turtle-admin >/dev/null <<EOF
$USER_NAME ALL=(root) NOPASSWD: /usr/bin/systemctl restart spy-turtle.service
$USER_NAME ALL=(root) NOPASSWD: /usr/bin/systemctl reboot
$USER_NAME ALL=(root) NOPASSWD: /usr/bin/systemctl poweroff
$USER_NAME ALL=(root) NOPASSWD: /usr/bin/nmcli device wifi connect *
EOF

sudo chmod 440 /etc/sudoers.d/spy-turtle-admin
sudo visudo -cf /etc/sudoers.d/spy-turtle-admin
sudo systemctl daemon-reload
sudo systemctl enable spy-turtle.service
echo "Installed. Restart with: sudo systemctl restart spy-turtle.service"
