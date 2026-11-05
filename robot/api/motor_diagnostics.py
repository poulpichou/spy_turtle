from fastapi import APIRouter,HTTPException
from robot.api import actions
from robot.system.runtime import get_robot
from robot.utils.logger import log

router=APIRouter(prefix="/admin/motors",tags=["Motor diagnostics"])

def get_motors():
    robot=get_robot()
    if robot is None or robot.motors is None:raise HTTPException(status_code=503,detail="Motors unavailable")
    if not hasattr(robot.motors,"driver"):raise HTTPException(status_code=503,detail="Hardware motor driver unavailable")
    return robot

@router.get("/pwm")
def pwm_status():
    robot=get_motors()
    return {"motors":robot.motors.status(),"pwm":robot.motors.driver.pwm_status()}

@router.post("/reset-pwm")
def reset_pwm():
    robot=get_motors()
    actions.disarm_motion()
    robot.state.motion="stop"
    try:
        result=robot.motors.reset_pwm()
        log.info("[MOTOR DIAG] PWM manually reset; motors stopped")
        return {"ok":True,"motors_stopped":True,"pwm":result}
    except Exception as error:
        log.error(f"[MOTOR DIAG] PWM reset error: {error}")
        raise HTTPException(status_code=500,detail=str(error)) from error
