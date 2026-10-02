# Spy Turtle optional OLED eyes

This patch makes the two OLED eye displays optional.

Current configuration after applying:

```python
EYES_ENABLED=False
OLED_LEFT_ADDRESS=0x3C
OLED_RIGHT_ADDRESS=0x3D
```

Behavior:
- `EYES_ENABLED=False`: no OLED I2C initialization is attempted.
- `EYES_ENABLED=True`: both OLEDs are initialized normally.
- If OLED initialization fails while enabled, Spy Turtle logs the error and continues with no-op displays instead of crashing.
- The `FaceController` remains active, so emotions and linked LED effects still work.

## Apply

Extract the ZIP directly inside the root of `spy_turtle`, then run:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\spy_turtle_eyes_optional\apply_patch.ps1
```

Then:

```powershell
git diff
git add -A
git commit -m "Make OLED eyes optional"
git push
```

To re-enable the eyes later:

```python
EYES_ENABLED=True
```
