from fastapi import APIRouter
from pydantic import BaseModel
from robot.system.runtime import get_robot
from fastapi import HTTPException

router=APIRouter(prefix="/sentinel",tags=["sentinel"])
class Toggle(BaseModel): enabled:bool

def instance():
    robot=get_robot()
    if robot is None or not hasattr(robot,"sentinel"):raise HTTPException(status_code=503,detail="Sentinel unavailable")
    return robot.sentinel

@router.get("/status")
def status():return instance().status()

@router.post("/enable")
def enable(value:Toggle):return instance().set_enabled(value.enabled)
