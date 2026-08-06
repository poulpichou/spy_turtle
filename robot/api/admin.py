import subprocess
from fastapi import APIRouter,HTTPException,Request
from pydantic import BaseModel,Field
from robot.utils.logger import log

router=APIRouter(prefix="/admin",tags=["admin"])

class WifiRequest(BaseModel):
    ssid:str=Field(min_length=1,max_length=64)
    password:str=Field(min_length=8,max_length=128)

def origin(request):
    forwarded=request.headers.get("x-forwarded-for")
    address=forwarded.split(",")[0].strip() if forwarded else request.client.host if request.client else "unknown"
    agent=request.headers.get("user-agent","unknown")
    return f"ip={address} agent={agent}"

def run(command,timeout=30):
    result=subprocess.run(command,capture_output=True,text=True,timeout=timeout,check=False)
    output=(result.stdout or result.stderr).strip()
    if result.returncode:raise HTTPException(status_code=500,detail=output or f"Command failed: {result.returncode}")
    return output

@router.post("/turtle/restart")
def restart_turtle(request:Request):
    log.warn(f"[ADMIN] restart turtle requested {origin(request)}")
    subprocess.Popen(["sudo","systemctl","restart","spy-turtle.service"],start_new_session=True)
    return {"ok":True,"message":"Spy Turtle restart scheduled"}

@router.post("/system/reboot")
def reboot(request:Request):
    log.warn(f"[ADMIN] reboot requested {origin(request)}")
    subprocess.Popen(["sudo","systemctl","reboot"],start_new_session=True)
    return {"ok":True,"message":"Reboot scheduled"}

@router.post("/system/shutdown")
def shutdown(request:Request):
    log.warn(f"[ADMIN] shutdown requested {origin(request)}")
    subprocess.Popen(["sudo","systemctl","poweroff"],start_new_session=True)
    return {"ok":True,"message":"Shutdown scheduled"}

@router.post("/wifi")
def add_wifi(data:WifiRequest,request:Request):
    log.info(f"[ADMIN] add Wi-Fi ssid={data.ssid} requested {origin(request)}")
    output=run(["sudo","nmcli","device","wifi","connect",data.ssid,"password",data.password])
    return {"ok":True,"message":output or "Wi-Fi connection added"}
