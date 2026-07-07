from software.core.state import STATE

def move_forward():
    STATE.x += 1

def move_backward():
    STATE.x -= 1

def turn_left():
    STATE.angle -= 10

def turn_right():
    STATE.angle += 10

def set_emotion(emotion: str):
    STATE.emotion = emotion

def set_led(mode: str):
    STATE.led_mode = mode