# Thermal/Admin/PWA/HTTPS update

The Admin tab is a simple local passthrough for a fixed list of commands:

- `sudo -n reboot`
- `sudo -n shutdown now`
- `sudo -n nmcli device wifi connect ...`
- restart Spy Turtle through the existing stop/start scripts

No token, daemon, service installation or arbitrary shell endpoint is added.

Each request is logged with its source IP. Reboot, shutdown and restart require frontend confirmation.

## Windows

```powershell
Expand-Archive -Path "$HOME\Downloads\spy_turtle_thermal_admin_passthrough.zip" -DestinationPath . -Force
python .\apply_update.py
git diff
git add .
git commit -m "Add thermal view and simple admin passthrough"
git push
```

## Raspberry Pi

```bash
cd ~/spy_turtle
git pull
chmod +x scripts/check_https.sh
./scripts/stop_turtle.sh
./scripts/start_turtle.sh
./scripts/check_https.sh
```

The Thermal tab mirrors the RGB camera until the USB thermal camera arrives.
