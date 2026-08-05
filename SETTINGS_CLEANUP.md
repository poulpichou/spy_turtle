# Settings cleanup

All GPIO and I2C allocations are now centralized in `robot/config/settings.py`.

Delete the obsolete file:

```text
robot/config/motors.py
```

The servo movement calibration remains in `robot/config/servos.json`, but its GPIO allocation has moved to `settings.py`.

Important: the current wiring assigns GPIO18 to both the WS2812 LED device and the MAX98357A BCLK signal. This update preserves the existing configuration instead of silently changing hardware wiring, but the conflict should be resolved before relying on LEDs and audio simultaneously.
