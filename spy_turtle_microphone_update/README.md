# Spy Turtle USB microphone update

Validated microphone:
- Texas Instruments PCM2902 (`08bb:2902`)
- ALSA card: `Device` / `USB PnP Sound Device`
- Capture device: `plughw:CARD=Device,DEV=0`
- S16_LE, 16 kHz, mono

The patch enables the microphone, adds `/audio/microphone/status`, includes microphone state in `/health`, keeps the existing frontend Listen stream, adds `scripts/test_microphone.sh`, documents the validated device, and changes the touchscreen navigation symbols to ASCII `<-`, `<<`, `>>`.

Apply from the root of `spy_turtle`:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\spy_turtle_microphone_update\apply_patch.ps1
```

Then:

```powershell
git diff
git add -A
git commit -m "Integrate USB microphone"
git push
```

On the Pi:

```bash
cd ~/spy_turtle
git pull
bash scripts/test_microphone.sh
python -m robot.startup.main
```

While Spy Turtle is running:

```bash
curl -s http://localhost:8000/audio/microphone/status
```
