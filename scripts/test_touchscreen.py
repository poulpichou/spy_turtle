#!/usr/bin/env python3
import time
from robot.hardware.touchscreen import Touchscreen

touch=Touchscreen()
print("status:",touch.status())
if not touch.available:
    raise SystemExit("No supported touchscreen detected.")
print("Touch the screen. Ctrl+C to stop.")
try:
    while True:
        point=touch.poll()
        if point is not None:print("touch:",point,flush=True)
        time.sleep(0.02)
except KeyboardInterrupt:
    pass
finally:
    touch.close()
