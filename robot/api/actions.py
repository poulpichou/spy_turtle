from robot.system.runtime import get_robot
from robot.utils.logger import log


def move_forward():
    robot=get_robot()
    log.info("[API] move forward")
    robot.motors.forward()
    robot.state.x+=1

def move_backward():
    robot=get_robot()
    log.info("[API] move backward")
    robot.motors.backward()
    robot.state.x-=1

def turn_left():
    robot=get_robot()
    log.info("[API] turn left")
    robot.motors.turn_left()
    robot.state.angle-=10

def turn_right():
    robot=get_robot()
    log.info("[API] turn right")
    robot.motors.turn_right()
    robot.state.angle+=10

def stop():
    robot=get_robot()
    log.info("[API] stop")
    robot.motors.stop()

def set_emotion(emotion):
    robot=get_robot()
    log.info(f"[API] emotion {emotion}")
    robot.state.emotion=emotion
    if robot.face:
        robot.face.play(emotion)

def set_led(mode):
    robot=get_robot()
    log.info(f"[API] led {mode}")
    if robot.leds:
        robot.leds.set_mode(mode)
    robot.state.led_mode=mode

def camera_start():
    robot=get_robot()
    log.info("[API] camera start")
    robot.camera.start()

def camera_stop():
    robot=get_robot()
    log.info("[API] camera stop")
    robot.camera.stop()

def camera_frame():
    robot=get_robot()
    return robot.camera.get_frame()

def speak(text):
    robot=get_robot()
    log.info(f"[API] speak {text}")
    if robot.speaker:
        robot.speaker.play(text)

def look_left():
    robot=get_robot()
    log.info("[API] camera left")
    robot.servo.look_left()

def look_right():
    robot=get_robot()
    log.info("[API] camera right")
    robot.servo.look_right()

def look_up():
    robot=get_robot()
    log.info("[API] camera up")
    robot.servo.look_up()

def look_down():
    robot=get_robot()
    log.info("[API] camera down")
    robot.servo.look_down()

def camera_center():
    robot=get_robot()
    log.info("[API] camera center")
    robot.servo.center()

def shell_mode(mode):
    robot=get_robot()
    log.info(f"[API] shell mode {mode}")
    if robot and robot.shell:
        robot.shell.set_mode(mode)

def shell_event(event):
    robot=get_robot()
    log.info(f"[API] shell event {event}")
    if robot and robot.shell:
        robot.shell.trigger(event)

def shell_text(text,color=None):
    robot=get_robot()
    log.info(f"[API] shell text {text}")
    if robot and robot.shell:
        robot.shell.send_text(text,color)