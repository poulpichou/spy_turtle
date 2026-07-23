import os
import shutil
from datetime import datetime
from pathlib import Path
from fastapi import FastAPI,HTTPException,Query
from fastapi.responses import FileResponse,Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel,Field
from robot.api import actions
from robot.assets.assets import get_assets
from robot.system.runtime import get_robot
from robot.utils.logger import log

app=FastAPI()
ROOT=Path(__file__).parent.parent.parent
FRONTEND=ROOT/"frontend"
PHOTOS=ROOT/"photos"
PHOTOS.mkdir(exist_ok=True)

class Command(BaseModel):
    type:str
    value:str=""
    extra:dict=Field(default_factory=dict)

def servo_status(robot):
    if robot is None or robot.servo is None or not hasattr(robot.servo,"status"):return None
    return safe_call(robot.servo.status)

def state():
    robot=get_robot()
    if robot is None:return {"error":"no robot"}
    data=robot.state.to_dict()
    data["servo"]=servo_status(robot)
    return data

def safe_call(function,default=None,digits=None):
    try:
        value=function()
        if digits is not None and isinstance(value,(int,float)):value=round(value,digits)
        return value
    except Exception:
        return default

def cpu_temperature():
    path=Path("/sys/class/thermal/thermal_zone0/temp")
    if not path.exists():return None
    return round(float(path.read_text().strip())/1000,1)

def uptime_seconds():
    path=Path("/proc/uptime")
    if not path.exists():return None
    return round(float(path.read_text().split()[0]),1)

@app.get("/state")
def get_state(): return state()

@app.get("/health")
def get_health():
    robot=get_robot()
    if robot is None:raise HTTPException(status_code=503,detail="Robot is not initialized")
    disk=shutil.disk_usage(ROOT)
    battery=robot.battery
    return {
        "ok":True,
        "timestamp":datetime.now().isoformat(),
        "system":{
            "uptime_seconds":uptime_seconds(),
            "cpu_temperature_c":cpu_temperature(),
            "load_1m":round(os.getloadavg()[0],2) if hasattr(os,"getloadavg") else None,
            "disk_free_gb":round(disk.free/(1024**3),1),
            "disk_total_gb":round(disk.total/(1024**3),1)
        },
        "battery":{
            "level_percent":safe_call(battery.get_level,digits=1),
            "voltage_v":safe_call(battery.get_voltage,digits=2),
            "current_a":safe_call(battery.get_current,digits=2),
            "cells":safe_call(battery.get_cells),
            "remaining_capacity":safe_call(battery.get_remaining_capacity),
            "charging":safe_call(battery.is_charging),
            "usb_connected":safe_call(battery.usb_connected)
        },
        "robot":{
            "emotion":robot.state.emotion,
            "motion":robot.state.motion,
            "led_mode":robot.state.led_mode,
            "shell_mode":robot.state.shell_mode,
            "camera_on":robot.state.camera_on,
            "idle_seconds":round(robot.state.idle_seconds(),1),
            "last_interaction_type":robot.state.last_interaction_type,
            "interaction_count":robot.state.interaction_count,
            "servo":servo_status(robot),
            "components":{
                "motors":robot.motors is not None,
                "face":robot.face is not None,
                "leds":robot.leds is not None,
                "camera":robot.camera is not None,
                "battery":robot.battery is not None,
                "speaker":robot.speaker is not None,
                "servo":robot.servo is not None,
                "shell":robot.shell is not None
            }
        }
    }

@app.get("/assets")
def get_available_assets(): return {section:build_assets(section) for section in ("shell","eyes","leds","audio")}

def build_assets(section):
    return [{"name":name,"label":asset.get("label",name)} for name,asset in get_assets(section).items() if asset.get("available",True)]

@app.get("/logs")
def get_logs(count:int=Query(default=80,ge=1,le=100)): return {"lines":list(log.tail(count))}

@app.get("/photos")
def get_photos():
    files=sorted([path for path in PHOTOS.iterdir() if path.suffix.lower() in {".jpg",".jpeg",".png"}],key=lambda path:path.stat().st_mtime,reverse=True)
    return {"photos":[{"name":path.name,"url":f"/photos/{path.name}"} for path in files]}

@app.post("/photos/capture")
def capture_photo():
    try:
        content=actions.camera_frame()
        name=datetime.now().strftime("%Y%m%d_%H%M%S_%f")+".jpg"
        path=PHOTOS/name
        path.write_bytes(content)
        log.info(f"[PHOTO] saved {name}")
        return {"name":name,"url":f"/photos/{name}"}
    except Exception as error:
        log.error(f"[PHOTO ERROR] {error}")
        raise HTTPException(status_code=500,detail=str(error)) from error

@app.get("/photos/{name}")
def get_photo(name:str):
    path=(PHOTOS/name).resolve()
    if path.parent!=PHOTOS.resolve() or not path.is_file():raise HTTPException(status_code=404,detail="Photo not found")
    return FileResponse(path)

@app.post("/command")
def command(cmd:Command):
    log.info(f"[API] command {cmd.type} {cmd.value}")
    try:
        if cmd.type=="move":
            if cmd.value=="forward":actions.move_forward()
            elif cmd.value=="backward":actions.move_backward()
            elif cmd.value=="left":actions.turn_left()
            elif cmd.value=="right":actions.turn_right()
            elif cmd.value=="stop":actions.stop()
            else:raise ValueError(f"Unknown movement: {cmd.value}")
        elif cmd.type=="face":actions.set_emotion(cmd.value)
        elif cmd.type=="led":actions.set_led(cmd.value)
        elif cmd.type=="shell":actions.shell_show(cmd.value)
        elif cmd.type=="shell_text":actions.shell_text(cmd.value)
        elif cmd.type=="head":
            if cmd.value=="left":actions.look_left()
            elif cmd.value=="right":actions.look_right()
            elif cmd.value=="up":actions.look_up()
            elif cmd.value=="down":actions.look_down()
            elif cmd.value=="center":actions.camera_center()
            else:raise ValueError(f"Unknown head command: {cmd.value}")
        elif cmd.type=="sound":actions.speak(cmd.value)
        else:raise ValueError(f"Unknown command type: {cmd.type}")
    except Exception as error:
        log.error(f"[API ERROR] {error}")
        raise HTTPException(status_code=400,detail=str(error)) from error
    return state()

@app.get("/camera/frame")
def camera_frame(): return Response(content=actions.camera_frame(),media_type="image/jpeg")

@app.post("/camera/start")
def camera_start():
    actions.camera_start()
    return state()

@app.post("/camera/stop")
def camera_stop():
    actions.camera_stop()
    return state()

app.mount("/",StaticFiles(directory=FRONTEND,html=True),name="frontend")
