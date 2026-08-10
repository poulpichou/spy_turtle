import subprocess
from pathlib import Path
from fastapi import APIRouter,HTTPException,Request
from pydantic import BaseModel,Field
from robot.system.runtime import get_robot
from robot.utils.logger import log

router=APIRouter(prefix="/admin",tags=["admin"])
ROOT=Path(__file__).resolve().parents[2]

class WifiRequest(BaseModel):
    ssid:str=Field(min_length=1,max_length=64)
    password:str=Field(min_length=8,max_length=128)
class VolumeRequest(BaseModel): volume:int=Field(ge=0,le=100)
class ToggleRequest(BaseModel): enabled:bool
class ComponentRequest(BaseModel):
    component:str
    enabled:bool
class SensitivityRequest(BaseModel): sensitivity:int=Field(ge=0,le=100)

def source(request):
    forwarded=request.headers.get("x-forwarded-for")
    ip=forwarded.split(",")[0].strip() if forwarded else request.client.host if request.client else "unknown"
    return f"ip={ip}"
def detached(command): subprocess.Popen(command,cwd=ROOT,start_new_session=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
def robot_or_503():
    robot=get_robot()
    if robot is None:raise HTTPException(status_code=503,detail="Robot unavailable")
    return robot

@router.post("/turtle/restart")
def restart_turtle(request:Request):
    log.warn(f"[ADMIN] restart turtle {source(request)}");detached(["bash","-lc","sleep 1; ./scripts/stop_turtle.sh; sleep 1; ./scripts/start_turtle.sh"]);return {"ok":True,"message":"Spy Turtle restart requested"}
@router.post("/system/reboot")
def reboot(request:Request):
    log.warn(f"[ADMIN] sudo reboot {source(request)}");detached(["sudo","-n","reboot"]);return {"ok":True,"message":"Reboot requested"}
@router.post("/system/shutdown")
def shutdown(request:Request):
    log.warn(f"[ADMIN] sudo shutdown now {source(request)}");detached(["sudo","-n","shutdown","now"]);return {"ok":True,"message":"Shutdown requested"}
@router.post("/wifi")
def add_wifi(data:WifiRequest,request:Request):
    log.info(f"[ADMIN] add Wi-Fi ssid={data.ssid} {source(request)}");detached(["sudo","-n","nmcli","device","wifi","connect",data.ssid,"password",data.password]);return {"ok":True,"message":"Wi-Fi command sent"}

@router.get("/audio/volume")
def get_volume():
    robot=robot_or_503()
    if robot.speaker is None:raise HTTPException(status_code=503,detail="Speaker unavailable")
    return {"ok":True,**robot.speaker.status()}
@router.post("/audio/volume")
def set_volume(data:VolumeRequest,request:Request):
    robot=robot_or_503()
    if robot.speaker is None:raise HTTPException(status_code=503,detail="Speaker unavailable")
    robot.speaker.set_volume(data.volume);log.info(f"[ADMIN] speaker volume={data.volume}% {source(request)}")
    return {"ok":True,"volume":robot.speaker.volume,"message":f"Volume set to {robot.speaker.volume}%"}

@router.get("/power")
def get_power(): return {"ok":True,**robot_or_503().power.status()}
@router.post("/power/component")
def set_power_component(data:ComponentRequest,request:Request):
    try:state=robot_or_503().power.set_component(data.component,data.enabled)
    except (ValueError,RuntimeError) as error:raise HTTPException(status_code=400,detail=str(error)) from error
    log.info(f"[ADMIN] power {data.component}={data.enabled} {source(request)}")
    return {"ok":True,**state}
@router.post("/power/idle")
def set_idle(data:ToggleRequest,request:Request):
    state=robot_or_503().power.set_idle(data.enabled);log.info(f"[ADMIN] idle={data.enabled} {source(request)}");return {"ok":True,**state}
@router.post("/audio/microphone-sensitivity")
def set_microphone_sensitivity(data:SensitivityRequest,request:Request):
    state=robot_or_503().power.set_microphone_sensitivity(data.sensitivity)
    log.info(f"[ADMIN] microphone sensitivity={data.sensitivity}% display-only {source(request)}")
    return {"ok":True,**state}
