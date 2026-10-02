# Spy Turtle touchscreen UI

This patch adds the first capacitive-touch UI for the ST7796 back screen while reusing the existing shell rendering and robot actions.

## UI

First touch on any normal shell view opens the touchscreen Home page. That first touch never triggers a command.

Home:
- Status
- Logs
- Commands
- Admin
- Idle mode

Commands:
- Face
- LEDs
- Screen
- Sound

Each command opens a generic paginated selection view populated from the existing asset catalog, so newly added resources automatically appear without adding buttons by hand.

Admin:
- Volume - / +
- Known Wi-Fi networks
- Idle mode
- Safe shutdown with confirmation
- Back

Adding a brand-new Wi-Fi network remains in the web frontend; the back screen only reconnects to already saved networks.

When Idle mode is enabled, touchscreen polling remains active. Touching the screen disables Idle mode and opens Home.

## Touch controller support

The driver auto-detects:
- FT6x36 / FT6336 family at I2C `0x38`
- GT911 family at I2C `0x5D` or `0x14`

No touch-controller address is hardcoded into the normal robot configuration.

## Apply

Extract directly inside `spy_turtle`, then from the repository root:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\spy_turtle_touch_ui\apply_patch.ps1
```

Review:

```powershell
git diff
git status
```

Commit when ready:

```powershell
git add -A
git commit -m "Add ST7796 touchscreen UI"
git push
```

## First hardware test

After pulling on the Raspberry Pi, stop Spy Turtle first so two processes do not try to own GPIO23 / the I2C touchscreen simultaneously.

Then:

```bash
cd ~/spy_turtle
source .venv/bin/activate
python scripts/test_touchscreen.py
```

Expected startup output resembles one of:

```text
status: {'available': True, 'controller': 'ft6x36', 'address': '0x38', ...}
```

or:

```text
status: {'available': True, 'controller': 'gt911', 'address': '0x5D', ...}
```

Touch several locations. The test prints:

```text
touch: (x, y)
```

Useful calibration targets:
- top-left should be near `(0, 0)`
- top-right near `(319, 0)`
- bottom-left near `(0, 479)`
- bottom-right near `(319, 479)`

If axes are reversed or mirrored, change only these settings:

```python
ST7796_CTP_SWAP_XY=False
ST7796_CTP_INVERT_X=False
ST7796_CTP_INVERT_Y=False
```

Do not tune the UI hitboxes until coordinates are correct.

## Full robot test

Once coordinates are correct:

```bash
python -m robot.startup.main
```

Expected behavior:
1. normal back-screen view appears;
2. first touch opens `HOME`;
3. touching `STATUS` or `LOGS` opens the existing views;
4. touching either of those existing non-touch views again returns to `HOME`;
5. `COMMANDS` opens data-driven Face / LEDs / Screen / Sound selectors;
6. `ADMIN` exposes volume, known Wi-Fi, Idle and shutdown;
7. enabling Idle turns off the normal powered components; touching the screen exits Idle and returns to Home.
