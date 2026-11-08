import time
import lgpio
from fastapi import APIRouter,HTTPException
from gpiozero import PWMOutputDevice
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

@router.post('/diagnose-direct-pwm')
def diagnose_direct_pwm():
    """Temporarily release PWMA and test raw lgpio in this same process, with motor standby disabled."""
    robot=get_motors();motors=robot.motors
    actions.disarm_motion()
    with motors._lock:
        driver=motors.driver
        if driver._closed:raise HTTPException(status_code=503,detail='Motor driver closed')
        try:
            motors.stop()
            robot.state.motion='stop'
            driver.standby.off()
            driver.ain1.off();driver.ain2.off();driver.bin1.off();driver.bin2.off()
        except Exception as error:
            raise HTTPException(status_code=500,detail=f'Cannot safely stop motors: {error}') from error
        gpio=driver.pwma_pin
        result={'gpio':gpio,'frequency_hz':1000,'duty_percent':50,'duration_seconds':1.5,
                'standby_disabled':True,'high_samples':0,'low_samples':0,'tx_pwm_result':None,
                'tx_busy':None,'gpiozero_restored':False}
        chip=None;claimed=False;error=None
        try:
            driver.pwma.close()
            driver.pwma=None
            chip=lgpio.gpiochip_open(0)
            lgpio.gpio_claim_output(chip,gpio,0);claimed=True
            result['tx_pwm_result']=lgpio.tx_pwm(chip,gpio,1000,50)
            result['tx_busy']=lgpio.tx_busy(chip,gpio,lgpio.TX_PWM)
            end=time.monotonic()+1.5
            while time.monotonic()<end:
                value=lgpio.gpio_read(chip,gpio)
                if value:result['high_samples']+=1
                else:result['low_samples']+=1
                time.sleep(0.0005)
        except Exception as exc:
            error=exc
            result['error']=f'{type(exc).__name__}: {exc}'
        finally:
            if chip is not None:
                if claimed:
                    try:lgpio.tx_pwm(chip,gpio,0,0)
                    except Exception as exc:result['stop_error']=str(exc)
                    try:lgpio.gpio_free(chip,gpio)
                    except Exception as exc:result['free_error']=str(exc)
                try:lgpio.gpiochip_close(chip)
                except Exception as exc:result['chip_close_error']=str(exc)
            try:
                driver.pwma=PWMOutputDevice(driver.pwma_pin,frequency=driver.pwm_frequency,initial_value=0)
                driver.standby.on()
                result['gpiozero_restored']=True
            except Exception as exc:
                result['restore_error']=f'{type(exc).__name__}: {exc}'
                try:driver.standby.off()
                except Exception:pass
        result['observed_toggling']=result['high_samples']>0 and result['low_samples']>0
        result['ok']=error is None and result['gpiozero_restored'] and not any(k.endswith('_error') for k in result)
        log.info(f'[MOTOR DIAG] direct lgpio PWM result: {result}')
        return result
