import os
import shutil
from datetime import datetime
from pathlib import Path
from fastapi import FastAPI,HTTPException,Query
from fastapi.responses import FileResponse,Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel,Field
from robot.api import actions
from robot.api.admin import router as admin_router
from robot.assets.assets import get_assets
from robot.config import settings
from robot.system.https_status import get_https_status
from robot.system.runtime import get_robot
from robot.utils.logger import log

app=FastAPI()
app.include_router(admin_router)
ROOT=Path(__file__).parent.parent.parent
FRONTEND=ROOT/"frontend"
PHOTOS=ROOT/"photos"
PHOTOS.mkdir(exist_ok=True)
STARTED_AT=datetime.now().isoformat()

@app.middleware("http")
async def no_cache(request,call_next):
    response=await call_next(request)
    path=request.url.path
    if path=="/" or path.endswith((".html",".css",".js",".webmanifest","service-worker.js")):
        response.headers["Cache-Control"]="no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"]="no-cache"
        response.headers["Expires"]="0"
    return response

class Command(BaseModel):
    type:str
    value:str=""
    extra:dict=Field(default_factory=dict)

def safe_call(function,default=None,digits=None):
    try:
        value=function()
        if digits is not None and isinstance(value,(int,float)):value=round(value,digits)
        return value
    except Exception:return default

def servo_status(robot):
    if robot is None or robot.servo is None or not hasattr(robot.servo,"status"):return None
    return safe_call(robot.servo.status)

def motor_status(robot):
    if robot is None or robot.motors is None or not hasattr(robot.motors,"status"):return None
    return safe_call(robot.motors.status)

def thermal_status(robot):
    if robot is None or robot.thermal_camera is None or not hasattr(robot.thermal_camera,"status"):return {"available":False}
    return safe_call(robot.thermal_camera.status,{"available":False})

def state():
    robot=get_robot()
    if robot is None:return {"error":"no robot"}
    data=robot.state.to_dict()
    data["servo"]=servo_status(robot)
    data["motors"]=motor_status(robot)
    data["thermal"]=thermal_status(robot)
    return data

def cpu_temperature():
    path=Path("/sys/class/thermal/thermal_zone0/temp")
    if not path.exists():return None
    return round(float(path.read_text().strip())/1000,1)

def uptime_seconds():
    path=Path("/proc/uptime")
    if not path.exists():return None
    return round(float(path.read_text().split()[0]),1)

@app.get("/state")
def get_state():return state()

@app.get("/version")
def get_version():return {"frontend":"2026.08.07.thermal1","started_at":STARTED_AT}

@app.get("/motors/config")
def get_motor_config():
    return {
        "drive_speed":settings.MOTOR_DRIVE_SPEED,"turn_speed":settings.MOTOR_TURN_SPEED,
        "speed_step":settings.MOTOR_SPEED_STEP,"min_speed":settings.MOTOR_MIN_SPEED,"max_speed":settings.MOTOR_MAX_SPEED,
        "wheel_diameter_mm":settings.MOTOR_WHEEL_DIAMETER_MM,"track_width_mm":settings.MOTOR_TRACK_WIDTH_MM,
        "encoder_pulses_per_rev":settings.MOTOR_ENCODER_PULSES_PER_REV,
        "distance_step_mm":settings.MOTOR_DISTANCE_STEP_MM,"turn_step_degrees":settings.MOTOR_TURN_STEP_DEGREES
    }

@app.get("/thermal/status")
def get_thermal_status():
    robot=get_robot()
    if robot is None:raise HTTPException(status_code=503,detail="Robot is not initialized")
    return thermal_status(robot)

@app.get("/health")
def get_health():
    robot=get_robot()
    if robot is None:raise HTTPException(status_code=503,detail="Robot is not initialized")
    disk=shutil.disk_usage(ROOT)
    current=state()
    return {
        "ok":True,"timestamp":datetime.now().isoformat(),"https":get_https_status(),
        "system":{"uptime_seconds":uptime_seconds(),"cpu_temperature_c":cpu_temperature(),"load_1m":round(os.getloadavg()[0],2) if hasattr(os,"getloadavg") else None,"disk_free_gb":round(disk.free/(1024**3),1),"disk_total_gb":round(disk.total/(1024**3),1)},
        "battery":current["battery"],
        "robot":{"brain":current["brain"],"camera":current["camera"],"thermal":current["thermal"],"motion":current["motion"],"motors":current["motors"],"shell":current["shell"],"leds":current["leds"],"servo":current["servo"],"components":{"motors":robot.motors is not None,"face":robot.face is not None,"leds":robot.leds is not None,"camera":robot.camera is not None,"thermal_camera":robot.thermal_camera is not None,"battery":robot.battery is not None,"speaker":robot.speaker is not None,"servo":robot.servo is not None,"shell":robot.shell is not None}}
    }

@app.get("/assets")
def get_available_assets():return {section:build_assets(section) for section in ("shell","eyes","leds","audio")}
def build_assets(section):return [{"name":name,"label":asset.get("label",name)} for name,asset in get_assets(section).items() if asset.get("available",True)]

@app.get("/logs")
def get_logs(count:int=Query(default=80,ge=1,le=100)):return {"lines":list(log.tail(count))}

@app.get("/photos")
def get_photos():
    found=sorted([path for path in PHOTOS.iterdir() if path.suffix.lower() in {".jpg",".jpeg",".png"}],key=lambda path:path.stat().st_mtime,reverse=True)
    return {"photos":[{"name":path.name,"url":f"/photos/{path.name}"} for path in found]}

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
            speed=cmd.extra.get("speed")
            if speed is not None:speed=float(speed)
            if cmd.value=="forward":actions.move_forward(speed)
            elif cmd.value=="backward":actions.move_backward(speed)
            elif cmd.value=="left":actions.turn_left(speed)
            elif cmd.value=="right":actions.turn_right(speed)
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
def camera_frame():return Response(content=actions.camera_frame(),media_type="image/jpeg",headers={"Cache-Control":"no-store"})

@app.get("/thermal/frame")
def thermal_frame():
    try:return Response(content=actions.thermal_frame(),media_type="image/jpeg",headers={"Cache-Control":"no-store","X-Thermal-Source":"mlx90640"})
    except Exception as error:
        log.warn(f"[THERMAL] frame failed, using RGB fallback: {error}")
        return Response(content=actions.camera_frame(),media_type="image/jpeg",headers={"Cache-Control":"no-store","X-Thermal-Fallback":"rgb-camera"})

@app.post("/camera/start")
def camera_start():actions.camera_start();return state()

@app.post("/camera/stop")
def camera_stop():actions.camera_stop();return state()

app.mount("/",StaticFiles(directory=FRONTEND,html=True),name="frontend")
