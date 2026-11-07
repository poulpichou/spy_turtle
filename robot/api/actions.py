import time
from threading import RLock
from robot.assets.assets import get_asset
from robot.config import settings
from robot.system.runtime import get_robot
from robot.utils.logger import log

def robot():
    instance=get_robot()
    if instance is None:raise RuntimeError("Robot is not initialized")
    return instance

def interact(kind):
    instance=robot()
    instance.state.touch(kind)
    if instance.state.sleeping_until:
        instance.state.sleeping_until=0.0
        if instance.brain and hasattr(instance.brain,"moods"):instance.brain.moods.choose("neutral")
        else:instance.state.emotion="neutral"
        if instance.face:instance.face.play("wake_up",force=True)
    return instance

_motion_lock=RLock()
_motion_deadline=0.0
MOTION_TIMEOUT=1.2

def arm_motion():
    global _motion_deadline
    with _motion_lock:_motion_deadline=time.monotonic()+MOTION_TIMEOUT

def disarm_motion():
    global _motion_deadline
    with _motion_lock:_motion_deadline=0.0

def motion_watchdog():
    global _motion_deadline
    with _motion_lock:
        if not _motion_deadline or time.monotonic()<_motion_deadline:return
        _motion_deadline=0.0
    instance=get_robot()
    if instance and instance.motors:
        instance.motors.stop();instance.state.motion="stop"
        log.warn("[SAFETY] Motion timeout: motors stopped")

def trace_actuator(kind,action):
    from robot.system.actuator_diagnostics import record
    r=robot();device=r.servo if kind=="SERVO" else r.motors
    try:status=device.status() if device else None
    except Exception as error:status={"error":str(error)}
    record(kind,f"{action} idle={r.power.idle_mode} status={status}")

def move_forward(speed=None):
    instance=interact("move_forward");log.info(f"[API] move forward speed={speed}");arm_motion();instance.motors.forward(speed);instance.state.motion="forward";trace_actuator("MOTOR","forward");instance.state.x+=settings.MOTOR_DISTANCE_STEP_MM
def move_backward(speed=None):
    instance=interact("move_backward");log.info(f"[API] move backward speed={speed}");arm_motion();instance.motors.backward(speed);instance.state.motion="backward";trace_actuator("MOTOR","backward");instance.state.x-=settings.MOTOR_DISTANCE_STEP_MM
def turn_left(speed=None):
    instance=interact("turn_left");log.info(f"[API] turn left speed={speed}");arm_motion();instance.motors.turn_left(speed);instance.state.motion="left";trace_actuator("MOTOR","left");instance.state.angle-=settings.MOTOR_TURN_STEP_DEGREES
def turn_right(speed=None):
    instance=interact("turn_right");log.info(f"[API] turn right speed={speed}");arm_motion();instance.motors.turn_right(speed);instance.state.motion="right";trace_actuator("MOTOR","right");instance.state.angle+=settings.MOTOR_TURN_STEP_DEGREES
def stop():
    instance=interact("stop");log.info("[API] stop");disarm_motion();instance.motors.stop();instance.state.motion="stop"

def move_joystick(left,right):
    import math
    left=float(left);right=float(right)
    if not math.isfinite(left) or not math.isfinite(right) or not (-1<=left<=1 and -1<=right<=1):raise ValueError("Joystick speeds must be finite and between -1 and 1")
    instance=interact("move_joystick")
    if abs(left)<0.01 and abs(right)<0.01:
        disarm_motion();instance.motors.stop();instance.state.motion="stop";return
    arm_motion()
    scale=float(getattr(settings,"MOTOR_JOYSTICK_MAX_SPEED",0.65))
    instance.motors.joystick(left*scale,right*scale)
    instance.state.motion="joystick"

def set_emotion(emotion):
    instance=interact(f"face:{emotion}")
    log.info(f"[API] face {emotion}")
    if not instance.face:raise RuntimeError("Face controller is unavailable")
    instance.face.user_event(emotion,10.0)
    instance.state.face_event_until=instance.face.manual_until

def set_led(mode):
    instance=interact(f"led:{mode}")
    log.info(f"[API] led {mode}")
    if not instance.leds:raise RuntimeError("LED controller is unavailable")
    instance.leds.set_mode(mode)
    instance.state.led_mode=mode

def camera_start():
    instance=interact("camera_start");log.info("[API] camera start");instance.camera.start();instance.state.camera_on=True
def camera_stop():
    instance=interact("camera_stop");log.info("[API] camera stop");instance.camera.stop();instance.state.camera_on=False
def camera_frame(): return robot().camera.get_frame()
def thermal_frame():
    instance=robot()
    if not instance.thermal_camera:raise RuntimeError("Thermal camera is unavailable")
    return instance.thermal_camera.get_frame()

def speak(text):
    instance=interact(f"sound:{text}");log.info(f"[API] speak {text}")
    if instance.speaker:instance.speaker.play(text)

def look_left():
    log.info("[API] camera left");instance=interact("head_left")
    if instance.brain:instance.brain.moods.manual_head_override()
    instance.servo.look_left();trace_actuator("SERVO","left")
def look_right():
    log.info("[API] camera right");instance=interact("head_right")
    if instance.brain:instance.brain.moods.manual_head_override()
    instance.servo.look_right();trace_actuator("SERVO","right")
def look_up():
    log.info("[API] camera up");instance=interact("head_up")
    if instance.brain:instance.brain.moods.manual_head_override()
    instance.servo.look_up();trace_actuator("SERVO","up")
def look_down():
    log.info("[API] camera down");instance=interact("head_down")
    if instance.brain:instance.brain.moods.manual_head_override()
    instance.servo.look_down();trace_actuator("SERVO","down")
def camera_center():
    log.info("[API] camera center");instance=interact("head_center")
    if instance.brain:instance.brain.moods.manual_head_override()
    instance.servo.center();trace_actuator("SERVO","center")

def shell_show(value):
    instance=interact(f"shell:{value}")
    if not instance.shell:raise RuntimeError("Shell controller is unavailable")
    log.info(f"[API] shell {value}")
    if value=="status":instance.shell.show_status()
    elif value=="log":instance.shell.show_log()
    else:
        get_asset("shell",value)
        instance.shell.show_image(value)

def shell_text(text):
    instance=interact("shell_text")
    if not instance.shell:raise RuntimeError("Shell controller is unavailable")
    text=str(text).strip()
    if not text:raise ValueError("Shell text cannot be empty")
    log.info(f"[API] shell text {text}")
    instance.shell.show_text(text)
