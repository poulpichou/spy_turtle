import subprocess
import threading
import time
from pathlib import Path
from fastapi import APIRouter,HTTPException,Request
from pydantic import BaseModel,Field
from robot.config import settings
from robot.system.runtime import get_robot
from robot.system.wifi import wifi_manager
from robot.utils.logger import log

router=APIRouter(prefix='/admin',tags=['admin'])
ROOT=Path(__file__).resolve().parents[2]

class WifiRequest(BaseModel):
    nickname:str=Field(default='',max_length=64)
    ssid:str=Field(min_length=1,max_length=64)
    password:str=Field(min_length=8,max_length=128)
class WifiNetworkRequest(BaseModel): ssid:str=Field(min_length=1,max_length=64)
class VolumeRequest(BaseModel): volume:int=Field(ge=0,le=100)
class ToggleRequest(BaseModel): enabled:bool
class ComponentRequest(BaseModel):
    component:str
    enabled:bool
class SensitivityRequest(BaseModel): sensitivity:int=Field(ge=0,le=100)
class MotorSpeedRequest(BaseModel): speed:int=Field(ge=100,le=300)
class PanOffsetRequest(BaseModel): offset:float=Field(ge=-20,le=20)

@router.get('/servos/pan-center')
def get_pan_center():
    return {'offset':robot_or_503().servo.get_pan_center_offset()}
@router.post('/servos/pan-center')
def set_pan_center(data:PanOffsetRequest):
    try:return {'offset':robot_or_503().servo.set_pan_center_offset(data.offset)}
    except (OSError,ValueError,RuntimeError) as error:raise HTTPException(status_code=400,detail=str(error)) from error

def source(request):
    forwarded=request.headers.get('x-forwarded-for')
    ip=forwarded.split(',')[0].strip() if forwarded else request.client.host if request.client else 'unknown'
    return f'ip={ip}'
def detached(command): subprocess.Popen(command,cwd=ROOT,start_new_session=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
_gpio_restart_lock=threading.Lock()
_gpio_restart={'state':'idle','error':None,'started_at':None,'finished_at':None}

def _restart_gpio_worker():
    try:
        with (ROOT/'logs/gpio-restart.log').open('a',encoding='utf-8') as output:
            output.write(f'\n==== GPIO restart {time.strftime("%Y-%m-%d %H:%M:%S")} ====\n');output.flush()
            result=subprocess.run(['bash',str(ROOT/'scripts/gpio_server/restart_gpio.sh')],cwd=ROOT,stdout=output,stderr=subprocess.STDOUT,timeout=25)
        if result.returncode:raise RuntimeError(f'restart script exit={result.returncode}; see logs/gpio-restart.log')
        from robot.gpio_server.client import client
        client.call('motors','status',timeout=1.5)
        client.call('servo','status',timeout=1.5)
        client.call('servo','center',timeout=1.5) # Uses persisted pan offset
        with _gpio_restart_lock:_gpio_restart.update(state='ready',error=None,finished_at=time.time())
        log.info('[ADMIN] isolated GPIO restart completed')
    except Exception as error:
        with _gpio_restart_lock:_gpio_restart.update(state='failed',error=f'{type(error).__name__}: {error}',finished_at=time.time())
        log.error(f'[ADMIN] isolated GPIO restart failed: {error}')

@router.get('/turtle/reset/status')
def gpio_reset_status():
    with _gpio_restart_lock:return {'ok':_gpio_restart['state']!='failed',**_gpio_restart}

def robot_or_503():
    robot=get_robot()
    if robot is None:raise HTTPException(status_code=503,detail='Robot unavailable')
    return robot

# [SHELL DIAG PATCH]
@router.get('/diagnostics/shell')
def shell_diagnostics():
    from robot.shell.diagnostics import snapshot
    return snapshot(robot_or_503())

@router.post('/turtle/reset')
def reset_turtle(request:Request):
    from robot.system.robot_reset_manager import reset_manager
    from robot.config import settings
    if not settings.SIMULATION and getattr(settings,'GPIO_SERVER_ENABLED',False):
        from robot.api.actions import disarm_motion
        disarm_motion()
        robot=get_robot()
        if robot:robot.state.motion='stop'
        log.warn(f'[ADMIN] isolated GPIO restart requested {source(request)}')
        with _gpio_restart_lock:
            if _gpio_restart['state']=='restarting':raise HTTPException(status_code=409,detail='GPIO restart already in progress')
            _gpio_restart.update(state='restarting',error=None,started_at=time.time(),finished_at=None)
            threading.Thread(target=_restart_gpio_worker,daemon=True,name='gpio-restart').start()
        return {'ok':True,'state':'restarting','message':'GPIO server restart started'}
    log.warn(f'[ADMIN] full robot soft reset requested {source(request)}')
    try:return reset_manager.request(timeout=45)
    except RuntimeError as error:raise HTTPException(status_code=409,detail=str(error)) from error
    except TimeoutError as error:raise HTTPException(status_code=504,detail=str(error)) from error

@router.post('/turtle/restart')
def restart_turtle(request:Request):
    log.warn(f'[ADMIN] restart turtle {source(request)}');detached(['bash','-lc','sleep 1; ./scripts/stop_turtle.sh; sleep 1; ./scripts/start_turtle.sh']);return {'ok':True,'message':'Spy Turtle restart requested'}
@router.post('/system/reboot')
def reboot(request:Request):
    log.warn(f'[ADMIN] sudo reboot {source(request)}');detached(['sudo','-n','reboot']);return {'ok':True,'message':'Reboot requested'}
@router.post('/system/shutdown')
def shutdown(request:Request):
    log.warn(f'[ADMIN] sudo shutdown now {source(request)}');detached(['sudo','-n','shutdown','now']);return {'ok':True,'message':'Shutdown requested'}

@router.post('/wifi/authorize-current')
def authorize_current_wifi():
    try:return {'ok':True,**wifi_manager.authorize_current()}
    except Exception as error:raise HTTPException(status_code=400,detail=str(error)) from error

@router.get('/wifi')
def get_wifi():
    try:return {'ok':True,**wifi_manager.status()}
    except Exception as error:raise HTTPException(status_code=500,detail=str(error)) from error
@router.post('/wifi')
def add_wifi(data:WifiRequest,request:Request):
    log.info(f'[ADMIN] add Wi-Fi nickname={data.nickname or data.ssid} ssid={data.ssid} {source(request)}')
    try:network=wifi_manager.add(data.nickname,data.ssid,data.password)
    except Exception as error:raise HTTPException(status_code=400,detail=str(error)) from error
    return {'ok':True,'message':f"Wi-Fi saved: {network['nickname']}",**network}
@router.post('/wifi/connect')
def connect_wifi(data:WifiNetworkRequest,request:Request):
    log.info(f'[ADMIN] connect Wi-Fi ssid={data.ssid} {source(request)}')
    try:wifi_manager.connect(data.ssid)
    except Exception as error:raise HTTPException(status_code=400,detail=str(error)) from error
    return {'ok':True,'message':'Wi-Fi connection requested'}
@router.post('/wifi/delete')
def delete_wifi(data:WifiNetworkRequest,request:Request):
    log.info(f'[ADMIN] delete Wi-Fi ssid={data.ssid} {source(request)}')
    try:wifi_manager.delete(data.ssid)
    except Exception as error:raise HTTPException(status_code=400,detail=str(error)) from error
    return {'ok':True,'message':'Wi-Fi network deleted'}

@router.get('/network/degraded')
def get_degraded_network():
    from robot.bluetooth.server import _vision_streamer
    if _vision_streamer is None:raise HTTPException(status_code=503,detail='Bluetooth vision unavailable')
    return _vision_streamer.status()
@router.post('/network/degraded')
def set_degraded_network(data:ToggleRequest):
    from robot.bluetooth.server import _vision_streamer
    if _vision_streamer is None:raise HTTPException(status_code=503,detail='Bluetooth vision unavailable')
    return _vision_streamer.set_degraded(data.enabled)

@router.get('/audio/volume')
def get_volume():
    robot=robot_or_503()
    if robot.speaker is None:raise HTTPException(status_code=503,detail='Speaker unavailable')
    return {'ok':True,**robot.speaker.status()}
@router.post('/audio/volume')
def set_volume(data:VolumeRequest,request:Request):
    robot=robot_or_503()
    if robot.speaker is None:raise HTTPException(status_code=503,detail='Speaker unavailable')
    robot.speaker.set_volume(data.volume);log.info(f'[ADMIN] speaker volume={data.volume}% {source(request)}')
    return {'ok':True,'volume':robot.speaker.volume,'message':f'Volume set to {robot.speaker.volume}%'}

@router.get('/audio/diagnostics')
def audio_diagnostics():
    speaker=robot_or_503().speaker
    if not speaker:raise HTTPException(status_code=503,detail="Speaker unavailable")
    return {'ok':True,**speaker.status()}
@router.get('/audio/adaptive')
def get_adaptive():
    speaker=robot_or_503().speaker
    if not speaker:raise HTTPException(status_code=503,detail="Speaker unavailable")
    return {'ok':True,**speaker.adaptive_status()}
@router.post('/audio/adaptive')
def set_adaptive(data:ToggleRequest):
    speaker=robot_or_503().speaker
    if not speaker:raise HTTPException(status_code=503,detail="Speaker unavailable")
    return {'ok':True,**speaker.set_adaptive(data.enabled)}

class HeadlightIntensityRequest(BaseModel): intensity:int=Field(ge=0,le=100)
@router.get('/leds/headlights/intensity')
def get_headlight_intensity():
    r=robot_or_503()
    if not r.leds:raise HTTPException(status_code=503,detail="LEDs unavailable")
    return {"ok":True,"intensity":r.leds.headlights_intensity}
@router.post('/leds/headlights/intensity')
def set_headlight_intensity(data:HeadlightIntensityRequest):
    r=robot_or_503()
    if not r.leds:raise HTTPException(status_code=503,detail="LEDs unavailable")
    return {"ok":True,"intensity":r.leds.set_headlights_intensity(data.intensity)}

class LedBrightnessRequest(BaseModel): brightness:int=Field(ge=0,le=100)
@router.get('/leds/brightness')
def get_led_brightness():
    robot=robot_or_503()
    if robot.leds is None:raise HTTPException(status_code=503,detail='LEDs unavailable')
    return {'ok':True,'brightness':robot.leds.get_brightness_percent()}
@router.post('/leds/brightness')
def set_led_brightness(data:LedBrightnessRequest,request:Request):
    robot=robot_or_503()
    if robot.leds is None:raise HTTPException(status_code=503,detail='LEDs unavailable')
    value=robot.leds.set_brightness_percent(data.brightness)
    log.info(f'[ADMIN] LED intensity={value}% {source(request)}')
    return {'ok':True,'brightness':value,'message':f'LED intensity set to {value}%'}

class HeadlightColorRequest(BaseModel): color:str=Field(pattern=r"^#[0-9a-fA-F]{6}$")
@router.get('/leds/headlights/color')
def get_headlight_color():
    robot=robot_or_503()
    if robot.leds is None:raise HTTPException(status_code=503,detail='LEDs unavailable')
    return {'ok':True,'color':robot.leds.headlights_color}
@router.post('/leds/headlights/color')
def set_headlight_color(data:HeadlightColorRequest,request:Request):
    robot=robot_or_503()
    if robot.leds is None:raise HTTPException(status_code=503,detail='LEDs unavailable')
    color=robot.leds.set_headlights_color(data.color)
    log.info(f'[ADMIN] headlights color={color} {source(request)}')
    return {'ok':True,'color':color}

@router.get('/power')
def get_power(): return {'ok':True,**robot_or_503().power.status()}
@router.post('/power/component')
def set_power_component(data:ComponentRequest,request:Request):
    try:state=robot_or_503().power.set_component(data.component,data.enabled)
    except (ValueError,RuntimeError) as error:raise HTTPException(status_code=400,detail=str(error)) from error
    log.info(f'[ADMIN] power {data.component}={data.enabled} {source(request)}')
    return {'ok':True,**state}
@router.post('/power/idle')
def set_idle(data:ToggleRequest,request:Request):
    state=robot_or_503().power.set_idle(data.enabled);log.info(f'[ADMIN] idle={data.enabled} {source(request)}');return {'ok':True,**state}
@router.post('/audio/microphone-sensitivity')
def set_microphone_sensitivity(data:SensitivityRequest,request:Request):
    state=robot_or_503().power.set_microphone_sensitivity(data.sensitivity)
    log.info(f'[ADMIN] microphone sensitivity={data.sensitivity}% display-only {source(request)}')
    return {'ok':True,**state}

@router.get('/motors/correction')
def get_motor_correction():
    motors=robot_or_503().motors
    if motors is None:raise HTTPException(status_code=503,detail='Motors unavailable')
    try:
        state=motors.status().get('encoders',{})
        return {'ok':True,'available':bool(state.get('enabled')),'enabled':bool(state.get('correction_enabled')),'left':state.get('left'),'right':state.get('right'),'reason':None if state.get('enabled') else ('Encoders disabled in settings (MOTOR_ENCODERS_ENABLED=False)' if not settings.MOTOR_ENCODERS_ENABLED else 'Encoder initialization failed; check wiring and GPIO logs')}
    except Exception as error:raise HTTPException(status_code=503,detail=str(error)) from error
@router.post('/motors/correction')
def set_motor_correction(data:ToggleRequest,request:Request):
    motors=robot_or_503().motors
    if motors is None or not hasattr(motors,'set_correction_enabled'):raise HTTPException(status_code=503,detail='Motor correction unavailable')
    try:state=motors.set_correction_enabled(data.enabled)
    except (ValueError,RuntimeError) as error:raise HTTPException(status_code=409,detail=str(error)) from error
    log.info(f'[ADMIN] motor correction={state["correction_enabled"]} {source(request)}')
    return {'ok':True,'available':bool(state['enabled']),'enabled':bool(state['correction_enabled'])}

@router.get('/motors/speed')
def get_motor_speed():
    robot=robot_or_503()
    if robot.motors is None or not hasattr(robot.motors,'get_speed_percent'):raise HTTPException(status_code=503,detail='Motor speed control unavailable')
    return {'ok':True,'speed':robot.motors.get_speed_percent()}
@router.post('/motors/speed')
def set_motor_speed(data:MotorSpeedRequest,request:Request):
    robot=robot_or_503()
    if robot.motors is None or not hasattr(robot.motors,'set_speed_percent'):raise HTTPException(status_code=503,detail='Motor speed control unavailable')
    speed=robot.motors.set_speed_percent(data.speed)
    log.info(f'[ADMIN] motor speed={speed}% {source(request)}')
    return {'ok':True,'speed':speed,'message':f'Drive speed set to {speed}%'}