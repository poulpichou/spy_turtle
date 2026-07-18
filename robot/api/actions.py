from robot.system.runtime import get_robot

def move_forward():
    robot=get_robot()
    print("[API] move forward")
    robot.motors.forward()
    robot.state.x+=1

def move_backward():
    robot=get_robot()
    print("[API] move backward")
    robot.motors.backward()
    robot.state.x-=1

def turn_left():
    robot=get_robot()
    print("[API] turn left")
    robot.motors.turn_left()
    robot.state.angle-=10

def turn_right():
    robot=get_robot()
    print("[API] turn right")
    robot.motors.turn_right()
    robot.state.angle+=10

def stop():
    robot=get_robot()
    print("[API] stop")
    robot.motors.stop()

def set_emotion(emotion):
    robot=get_robot()
    print(f"[API] emotion {emotion}")
    robot.state.emotion=emotion
    robot.face.play(emotion)

def set_led(mode):
    robot=get_robot()
    print(f"[API] led {mode}")
    robot.leds.set_mode(mode)
    robot.state.led_mode=mode

def camera_start():
    robot=get_robot()
    print("[API] camera start")
    robot.camera.start()

def camera_stop():
    robot=get_robot()
    print("[API] camera stop")
    robot.camera.stop()

def camera_frame():
    robot=get_robot()
    return robot.camera.get_frame()

def speak(text):
    robot=get_robot()
    print(f"[API] speak:{text}")
    robot.speaker.play(text)

def look_left():
    robot=get_robot()
    print("[API] camera left")
    robot.servo.look_left()

def look_right():
    robot=get_robot()
    print("[API] camera right")
    robot.servo.look_right()

def look_up():
    robot=get_robot()
    print("[API] camera up")
    robot.servo.look_up()

def look_down():
    robot=get_robot()
    print("[API] camera down")
    robot.servo.look_down()

def camera_center():
    robot=get_robot()
    print("[API] camera center")
    robot.servo.center()


# Shell screen

def shell_mode(mode):
    robot=get_robot()

    if robot and robot.shell:
        print(f"[API] shell mode {mode}")
        robot.shell.set_mode(mode)


def shell_event(event):
    robot=get_robot()

    if robot and robot.shell:
        print(f"[API] shell event {event}")
        robot.shell.trigger(event)