import hmac,os,subprocess
from fastapi import APIRouter,Header,HTTPException
from pydantic import BaseModel,Field
from robot.utils.logger import log
router=APIRouter(prefix="/admin",tags=["admin"])
class WifiRequest(BaseModel):ssid:str=Field(min_length=1,max_length=64);password:str=Field(min_length=8,max_length=128)
def auth(token):
    expected=os.environ.get("SPY_TURTLE_ADMIN_TOKEN","")
    if not expected:raise HTTPException(503,"Admin token is not configured")
    if not token or not hmac.compare_digest(token,expected):raise HTTPException(401,"Invalid admin token")
def run(cmd,timeout=30):
    result=subprocess.run(cmd,capture_output=True,text=True,timeout=timeout,check=False)
    output=(result.stdout or result.stderr).strip()
    if result.returncode:raise HTTPException(500,output or f"Command failed: {result.returncode}")
    return output
@router.post("/turtle/restart")
def restart(x_admin_token:str|None=Header(None)):
    auth(x_admin_token);log.warn("[ADMIN] turtle restart requested")
    subprocess.Popen(["sudo","systemctl","restart","spy-turtle.service"],start_new_session=True)
    return {"ok":True,"message":"Restart scheduled"}
@router.post("/system/reboot")
def reboot(x_admin_token:str|None=Header(None)):
    auth(x_admin_token);log.warn("[ADMIN] reboot requested")
    subprocess.Popen(["sudo","systemctl","reboot"],start_new_session=True)
    return {"ok":True,"message":"Reboot scheduled"}
@router.post("/system/shutdown")
def shutdown(x_admin_token:str|None=Header(None)):
    auth(x_admin_token);log.warn("[ADMIN] shutdown requested")
    subprocess.Popen(["sudo","systemctl","poweroff"],start_new_session=True)
    return {"ok":True,"message":"Shutdown scheduled"}
@router.post("/wifi")
def wifi(req:WifiRequest,x_admin_token:str|None=Header(None)):
    auth(x_admin_token);log.info(f"[ADMIN] add Wi-Fi {req.ssid}")
    return {"ok":True,"message":run(["sudo","nmcli","device","wifi","connect",req.ssid,"password",req.password])}
