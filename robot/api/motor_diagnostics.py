from fastapi import APIRouter,HTTPException
from robot.api import actions
from robot.system.runtime import get_robot
from robot.utils.logger import log

router=APIRouter(prefix='/admin/motors',tags=['Actuator diagnostics'])

def get_motors():
    robot=get_robot()
    if robot is None or robot.motors is None:raise HTTPException(status_code=503,detail='Motors unavailable')
    if not hasattr(robot.motors,'driver'):raise HTTPException(status_code=503,detail='Hardware motor driver unavailable')
    return robot

def get_servos():
    robot=get_robot()
    if robot is None or robot.servo is None or not hasattr(robot.servo,'reset_gpio'):
        raise HTTPException(status_code=503,detail='Hardware servo controller unavailable')
    return robot

@router.get('/pwm')
def pwm_status():
    robot=get_motors()
    return {'motors':robot.motors.status(),'pwm':robot.motors.driver.pwm_status()}

@router.post('/reset-pwm')
def reset_pwm():
    robot=get_motors();actions.disarm_motion();robot.state.motion='stop'
    try:
        result=robot.motors.reset_pwm()
        log.info('[MOTOR DIAG] PWM manually reset; motors stopped')
        return {'ok':True,'motors_stopped':True,'pwm':result}
    except Exception as error:
        log.error(f'[MOTOR DIAG] PWM reset error: {error}')
        raise HTTPException(status_code=500,detail=str(error)) from error

@router.get('/servo-pwm')
def servo_pwm_status():return get_servos().servo.diagnostic()

@router.post('/reset-servo-pwm')
def reset_servo_pwm():
    robot=get_servos()
    try:
        result=robot.servo.reset_gpio()
        log.info('[SERVO DIAG] Servo GPIO handle manually reset')
        return {'ok':True,'servos_idle':True,'servo':result}
    except Exception as error:
        log.error(f'[SERVO DIAG] GPIO reset error: {error}')
        raise HTTPException(status_code=500,detail=str(error)) from error

@router.post('/reset-all-pwm')
def reset_all_pwm():
    robot=get_motors()
    if robot.servo is None or not hasattr(robot.servo,'reset_gpio'):
        raise HTTPException(status_code=503,detail='Hardware servo controller unavailable')
    actions.disarm_motion();robot.state.motion='stop'
    results={}
    try:
        results['motors']=robot.motors.reset_pwm()
        results['servo']=robot.servo.reset_gpio()
        log.info('[ACTUATOR DIAG] PWM motor and servo handles reset; motors stopped, servos idle')
        return {'ok':True,'motors_stopped':True,'servos_idle':True,'results':results}
    except Exception as error:
        log.error(f'[ACTUATOR DIAG] Combined reset error: {error}; completed={list(results)}')
        raise HTTPException(status_code=500,detail={'error':str(error),'completed':list(results)}) from error
