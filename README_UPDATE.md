# Thermal/Admin/PWA/HTTPS update

This simplified version has no admin token.

Admin is limited to:
- restart Spy Turtle
- reboot Raspberry Pi
- shut down Raspberry Pi
- add a Wi-Fi network

Reboot and shutdown require frontend confirmation. Every admin request is logged with its source IP and user agent. No arbitrary shell command endpoint exists.

## Windows

After extracting at repository root:

```powershell
python .\apply_update.py
git diff
```

## Raspberry Pi

```bash
git pull
chmod +x scripts/install_admin_service.sh scripts/check_https.sh
sudo ./scripts/install_admin_service.sh
sudo systemctl restart spy-turtle.service
./scripts/check_https.sh
```

The Thermal tab mirrors the RGB camera until the USB thermal camera arrives.
