# Spy Turtle servo cleanup

This patch keeps the existing startup-centering behavior, but makes servo configuration clearer and easier to reason about.

Changes:
- PAN logical range: -75° to +75°
- TILT logical range: -45° to +45°
- PAN center pulse: 1500 us
- TILT center pulse: 1500 us
- config field names now explicitly state degrees:
  - `center_angle_deg`
  - `minimum_angle_deg`
  - `maximum_angle_deg`
  - `step_deg`
  - `speed_deg_per_second`
- the 1000/2000 us hardware safety clamp is moved to top-level `safe_pulse_min_us` / `safe_pulse_max_us`
- runtime status still exposes the old `current`, `target`, `minimum`, `maximum` names so the existing frontend remains compatible
- runtime status also exposes `center_pulse_us` and `microseconds_per_degree`
- web Admin shows live PAN/TILT angle + pulse information
- touchscreen Admin gets a `HEAD INFO` page
- OLED eyes are re-enabled with `EYES_ENABLED=True`

## Important first start

TILT used to have `center_pulse_us=1650`. This patch changes it to the standard nominal center of `1500 us`.

Before the first start after applying this patch:
1. loosen/remove the head linkage from the servos;
2. start Spy Turtle and let both servos center;
3. mechanically align the head;
4. reattach the linkage.

This makes the physical center correspond to 0° / 1500 us.

## Apply

Extract directly inside the root of `spy_turtle`, then:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\spy_turtle_servo_cleanup\apply_patch.ps1
```

Review:

```powershell
git diff
```

Commit:

```powershell
git add -A
git commit -m "Clarify servo calibration and ranges"
git push
```

On the Raspberry Pi:

```bash
cd ~/spy_turtle
git pull
source .venv/bin/activate
python -m robot.startup.main
```
