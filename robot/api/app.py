from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse
import time

from robot.system.runtime import get_robot
from robot.api import actions

app=FastAPI()

def state():
    robot=get_robot()
    return robot.state.__dict__ if robot else {"error":"no robot"}

@app.get("/state")
def get_state():
    return state()

@app.get("/battery")
def battery():
    robot=get_robot()
    if not robot:return {"error":"no robot"}
    return {"level":robot.battery.get_level(),"charging":robot.battery.is_charging()}

@app.post("/move/forward")
def forward():
    actions.move_forward()
    return state()

@app.post("/move/backward")
def backward():
    actions.move_backward()
    return state()

@app.post("/move/left")
def left():
    actions.turn_left()
    return state()

@app.post("/move/right")
def right():
    actions.turn_right()
    return state()

@app.post("/move/stop")
def stop():
    actions.stop()
    return state()

@app.post("/emotion/{emotion}")
def emotion(emotion:str):
    actions.set_emotion(emotion)
    return state()

@app.post("/led/{mode}")
def led(mode:str):
    actions.set_led(mode)
    return state()

@app.post("/camera/start")
def camera_start():
    actions.camera_start()
    return state()

@app.post("/camera/stop")
def camera_stop():
    actions.camera_stop()
    return state()

@app.get("/camera/frame")
def camera_frame():
    return {"frame":actions.camera_frame()}

@app.get("/camera/stream")
def camera_stream():
    def generate():
        while True:
            frame=actions.camera_frame()
            yield b"--frame\r\nContent-Type: image/jpeg\r\n\r\n"+frame+b"\r\n"
            time.sleep(0.05)
    return StreamingResponse(generate(),media_type="multipart/x-mixed-replace;boundary=frame")

@app.post("/camera/left")
def camera_left():
    actions.look_left()
    return state()

@app.post("/camera/right")
def camera_right():
    actions.look_right()
    return state()

@app.post("/camera/up")
def camera_up():
    actions.look_up()
    return state()

@app.post("/camera/down")
def camera_down():
    actions.look_down()
    return state()

@app.post("/camera/center")
def camera_center():
    actions.camera_center()
    return state()

@app.post("/shell/{mode}")
def shell(mode:str):
    actions.shell_mode(mode)
    return state()

@app.post("/shell/event/{event}")
def shell_event(event:str):
    actions.shell_event(event)
    return state()

@app.post("/speak/{text}")
def speak(text:str):
    actions.speak(text)
    return {"message":text}


app.mount("/",StaticFiles(directory="frontend",html=True),name="frontend")