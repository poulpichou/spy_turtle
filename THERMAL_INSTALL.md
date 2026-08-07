# MLX90640 thermal camera integration

This update replaces the RGB fallback in `/thermal/frame` with the physical MLX90640 at I2C address `0x33`.

- MLX90640 is optional: initialization failure does not prevent Spy Turtle from starting.
- `/thermal/frame` uses MLX90640 and falls back to RGB if a frame read fails.
- 32x24 temperatures are converted to a 320x240 JPEG using an Iron-style palette and bicubic interpolation.
- `/thermal/status`, `/state` and `/health` expose thermal status.
- Simulation gets a synthetic thermal image.
- The existing frontend Thermal tab already reads `/thermal/frame`, so no frontend structure changes are required.

Install:
```bash
cd ~/spy_turtle
source .venv/bin/activate
pip install adafruit-circuitpython-mlx90640
```

Check:
```bash
i2cdetect -y 1
python -c "import board,busio,adafruit_mlx90640; print('MLX library OK')"
```

Expected I2C devices: `2d`, `33`, `3c`, `3d`.

Then:
```bash
./scripts/stop_turtle.sh
./scripts/start_turtle.sh
tail -f logs/log
curl -s http://localhost:8000/thermal/status
curl -o /tmp/thermal.jpg http://localhost:8000/thermal/frame
file /tmp/thermal.jpg
```

If frame reads repeatedly fail, reduce `THERMAL_REFRESH_RATE_HZ` from `2` to `1`.
