# Thermal/Admin/PWA/HTTPS update

After extracting at repository root:

```powershell
python .\apply_update.py
git diff
```

On the Raspberry Pi:

```bash
git pull
chmod +x scripts/install_admin_service.sh scripts/check_https.sh
sudo ./scripts/install_admin_service.sh
sudo systemctl restart spy-turtle.service
./scripts/check_https.sh
```

The Thermal tab mirrors the RGB camera until the USB thermal camera arrives. Admin commands are allowlisted and token-protected; no arbitrary shell endpoint is exposed.
