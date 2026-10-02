#!/usr/bin/env python3
from pathlib import Path

ROOT=Path.cwd().resolve()
SETTINGS=ROOT/"robot"/"config"/"settings.py"
FACTORY=ROOT/"robot"/"factory"/"robot_factory.py"

for path in (SETTINGS,FACTORY):
    if not path.is_file():
        raise SystemExit(f"Expected file not found: {path}")

def read(path): return path.read_text(encoding="utf-8-sig")
def write(path,text): path.write_text(text,encoding="utf-8")

settings=read(SETTINGS)
if "EYES_ENABLED=" not in settings:
    marker="# OLED eyes (shared I2C bus)\n"
    if marker not in settings:
        raise SystemExit("Could not find OLED eyes section in robot/config/settings.py")
    settings=settings.replace(marker,marker+"EYES_ENABLED=False\n",1)
else:
    out=[]
    for line in settings.splitlines():
        out.append("EYES_ENABLED=False" if line.startswith("EYES_ENABLED=") else line)
    settings="\n".join(out)+("\n" if settings.endswith("\n") else "")
write(SETTINGS,settings)

factory=read(FACTORY)
import_line="from robot.hardware.null_eyes_display import NullEyesDisplay\n"
if import_line not in factory:
    marker="from robot.hardware.oled_display import OLEDDisplay\n"
    if marker not in factory:
        raise SystemExit("Could not find OLEDDisplay import in robot/factory/robot_factory.py")
    factory=factory.replace(marker,marker+import_line,1)

old = '        left_display=OLEDDisplay(settings.OLED_LEFT_ADDRESS,"left");right_display=OLEDDisplay(settings.OLED_RIGHT_ADDRESS,"right")\n        eyes_renderer=EyesRenderer(left_display,right_display);face=FaceController(eyes_renderer,leds)\n'
new = '''        left_display=NullEyesDisplay("left");right_display=NullEyesDisplay("right")
        if settings.EYES_ENABLED:
            try:
                left_display=OLEDDisplay(settings.OLED_LEFT_ADDRESS,"left");right_display=OLEDDisplay(settings.OLED_RIGHT_ADDRESS,"right")
            except Exception as error:
                log.error(f"[EYES] initialization failed, continuing without OLED eyes: {error}")
                left_display=NullEyesDisplay("left");right_display=NullEyesDisplay("right")
        else:log.info("[EYES] disabled by configuration")
        eyes_renderer=EyesRenderer(left_display,right_display);face=FaceController(eyes_renderer,leds)
'''
if old in factory:
    factory=factory.replace(old,new,1)
elif 'log.info("[EYES] disabled by configuration")' not in factory:
    raise SystemExit("Could not find expected OLED initialization block in robot/factory/robot_factory.py")
write(FACTORY,factory)

print("Updated robot/config/settings.py: EYES_ENABLED=False")
print("Updated robot/factory/robot_factory.py: optional/fallback OLED eyes")
