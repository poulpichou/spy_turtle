from robot.assets.assets import get_asset
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
        instance.state.emotion="neutral"
        if instance.face:instance.face.play("wake_up",force=True)
    return instance

def move_forward():
    instance=interact("move_forward")
    log.info("[API] move forward")
    instance.motors.forward()
    instance.state.motion="forward"
    instance.state.x+=1

def move_backward():
    instance=interact("move_backward")
    log.info("[API] move backward")
    instance.motors.backward()
    instance.state.motion="backward"
    instance.state.x-=1

def turn_left():
    instance=interact("turn_left")
    log.info("[API] turn left")
    instance.motors.turn_left()
    instance.state.motion="left"
    instance.state.angle-=10

def turn_right():
    instance=interact("turn_right")
    log.info("[API] turn right")
    instance.motors.turn_right()
    instance.state.motion="right"
    instance.state.angle+=10

def stop():
    instance=interact("stop")
    log.info("[API] stop")
    instance.motors.stop()
    instance.state.motion="stop"

def set_emotion(emotion):
    instance=interact(f"face:{emotion}")
    log.info(f"[API] face {emotion}")
    if not instance.face:raise RuntimeError("Face controller is unavailable")
    instance.face.user_event(emotion,10.0)
    instance.state.emotion=emotion
    instance.state.face_event_until=instance.face.manual_until

def set_led(mode):
    instance=interact(f"led:{mode}")
    log.info(f"[API] led {mode}")
    if not instance.leds:raise RuntimeError("LED controller is unavailable")
    instance.leds.set_mode(mode)
    instance.state.led_mode=mode

def camera_start():
    instance=interact("camera_start")
    log.info("[API] camera start")
    instance.camera.start()
    instance.state.camera_on=True

def camera_stop():
    instance=interact("camera_stop")
    log.info("[API] camera stop")
    instance.camera.stop()
    instance.state.camera_on=False

def camera_frame(): return robot().camera.get_frame()

def speak(text):
    instance=interact(f"sound:{text}")
    log.info(f"[API] speak {text}")
    if instance.speaker:instance.speaker.play(text)

def look_left():
    log.info("[API] camera left")
    interact("head_left").servo.look_left()

def look_right():
    log.info("[API] camera right")
    interact("head_right").servo.look_right()

def look_up():
    log.info("[API] camera up")
    interact("head_up").servo.look_up()

def look_down():
    log.info("[API] camera down")
    interact("head_down").servo.look_down()

def camera_center():
    log.info("[API] camera center")
    interact("head_center").servo.center()

def shell_show(value):
    instance=interact(f"shell:{value}")
    if not instance.shell:raise RuntimeError("Shell controller is unavailable")
    log.info(f"[API] shell {value}")
    if value=="status":instance.shell.show_status()
    elif value=="log":instance.shell.show_log()
    else:
        get_asset("shell",value)
        instance.shell.show_image(value)
    instance.state.shell_mode=value
    if instance.leds and hasattr(instance.leds,"linked_mode"):
        linked=instance.leds.linked_mode("shell",value)
        if linked:
            instance.leds.set_mode(linked)
            instance.state.led_mode=linked

def shell_text(text):
    instance=interact("shell_text")
    if not instance.shell:raise RuntimeError("Shell controller is unavailable")
    text=str(text).strip()
    if not text:raise ValueError("Shell text cannot be empty")
    log.info(f"[API] shell text {text}")
    instance.shell.show_text(text)
    instance.state.shell_mode="text"
