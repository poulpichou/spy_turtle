# Spy Turtle motion + camera Admin patch

Changes:
- PAN remains `-75° .. +75°` = 150° total.
- TILT becomes `-60° .. +60°` = 120° total.
- Removes the recently-added PAN/TILT debug line from web Admin.
- Adds **Drive speed** slider: 100–300%. 100% is the current speed (`0.30` drive / `0.25` turn); 300% requests x3 and the existing motor safety clamp still caps output at 1.0.
- Adds **Camera** slider: 2–10 fps, default 6 fps.
- Camera FPS is a frontend/browser setting and is persisted in `localStorage`.
- Motor speed is runtime state and resets to 100% when Spy Turtle restarts.

Apply from repository root:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\spy_turtle_motion_camera_admin\apply_patch.ps1
```

Then:

```powershell
git diff
git add -A
git commit -m "Add motion speed and camera refresh controls"
git push
```

On the Pi:

```bash
cd ~/spy_turtle
git pull
source .venv/bin/activate
python -m robot.startup.main
```

Reload/hard-refresh the frontend/PWA after deployment.
