from robot.assets.assets import get_asset
from robot.system.runtime import get_robot
from robot.utils.logger import log

def robot():
    instance=get_robot()
    if instance is None:raise RuntimeError("Robot is not initialized")
    return instance

def move_forward():
    instance=robot()
    log.info("[API] move forward")
    instance.motors.forward()
    instance.state.x+=1

def move_backward():
    instance=robot()
    log.info("[API] move backward")
    instance.motors.backward()
    instance.state.x-=1

def turn_left():
    instance=robot()
    log.info("[API] turn left")
    instance.motors.turn_left()
    instance.state.angle-=10

def turn_right():
    instance=robot()
    log.info("[API] turn right")
    instance.motors.turn_right()
    instance.state.angle+=10

def stop():
    instance=robot()
    log.info("[API] stop")
    instance.motors.stop()

def set_emotion(emotion):
    instance=robot()
    log.info(f"[API] face {emotion}")
    if not instance.face:raise RuntimeError("Face controller is unavailable")
    instance.face.play(emotion)
    instance.state.emotion=emotion

def set_led(mode):
    instance=robot()
    log.info(f"[API] led {mode}")
    if not instance.leds:raise RuntimeError("LED controller is unavailable")
    instance.leds.set_mode(mode)
    instance.state.led_mode=mode

def camera_start():
    instance=robot()
    log.info("[API] camera start")
    instance.camera.start()

def camera_stop():
    instance=robot()
    log.info("[API] camera stop")
    instance.camera.stop()

def camera_frame(): return robot().camera.get_frame()

def speak(text):
    instance=robot()
    log.info(f"[API] speak {text}")
    if instance.speaker:instance.speaker.play(text)

def look_left():
    log.info("[API] camera left")
    robot().servo.look_left()

def look_right():
    log.info("[API] camera right")
    robot().servo.look_right()

def look_up():
    log.info("[API] camera up")
    robot().servo.look_up()

def look_down():
    log.info("[API] camera down")
    robot().servo.look_down()

def camera_center():
    log.info("[API] camera center")
    robot().servo.center()

def shell_show(value):
    instance=robot()
    if not instance.shell:raise RuntimeError("Shell controller is unavailable")
    log.info(f"[API] shell {value}")
    if value=="status":
        instance.shell.show_status()
    elif value=="log":
        instance.shell.show_log()
    else:
        get_asset("shell",value)
        instance.shell.show_image(value)

def shell_text(text):
    instance=robot()
    if not instance.shell:raise RuntimeError("Shell controller is unavailable")
    text=str(text).strip()
    if not text:raise ValueError("Shell text cannot be empty")
    log.info(f"[API] shell text {text}")
    instance.shell.show_text(text)