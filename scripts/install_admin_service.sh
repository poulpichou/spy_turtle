#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
USER_NAME="${SUDO_USER:-$USER}"
read -rsp "New admin token (12+ chars): " TOKEN;echo
[[ ${#TOKEN} -ge 12 ]]||{ echo "Token too short";exit 1; }
sudo install -d -m 0750 /etc/spy-turtle
printf 'SPY_TURTLE_ADMIN_TOKEN=%q\n' "$TOKEN"|sudo tee /etc/spy-turtle/admin.env >/dev/null
sudo chmod 600 /etc/spy-turtle/admin.env
sudo tee /etc/systemd/system/spy-turtle.service >/dev/null <<EOF
[Unit]
Description=Spy Turtle
After=network-online.target
Wants=network-online.target
[Service]
Type=forking
User=$USER_NAME
WorkingDirectory=$ROOT
EnvironmentFile=/etc/spy-turtle/admin.env
ExecStart=$ROOT/scripts/start_turtle.sh
ExecStop=$ROOT/scripts/stop_turtle.sh
PIDFile=$ROOT/logs/robot.pid
Restart=on-failure
RestartSec=3
[Install]
WantedBy=multi-user.target
EOF
sudo tee /etc/sudoers.d/spy-turtle-admin >/dev/null <<EOF
$USER_NAME ALL=(root) NOPASSWD: /usr/bin/systemctl restart spy-turtle.service, /usr/bin/systemctl reboot, /usr/bin/systemctl poweroff
$USER_NAME ALL=(root) NOPASSWD: /usr/bin/nmcli device wifi connect *
EOF
sudo chmod 440 /etc/sudoers.d/spy-turtle-admin
sudo visudo -cf /etc/sudoers.d/spy-turtle-admin
sudo systemctl daemon-reload
sudo systemctl enable spy-turtle.service
echo "Installed. Run: sudo systemctl restart spy-turtle.service"
