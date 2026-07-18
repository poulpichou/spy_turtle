from fastapi import FastAPI
from robot.system.runtime import get_robot
from robot.api import actions
from fastapi.responses import StreamingResponse
import time
from fastapi.staticfiles import StaticFiles

app=FastAPI()
app.mount("/",StaticFiles(directory="frontend",html=True),name="frontend")

@app.get("/camera/stream")
def camera_stream():
    def generate():
        while True:
            frame=actions.camera_frame()
            yield(b"--frame\r\nContent-Type: image/jpeg\r\n\r\n"+frame+b"\r\n")
            time.sleep(0.05)

    return StreamingResponse(generate(),media_type="multipart/x-mixed-replace; boundary=frame")

def state():
    robot=get_robot()
    return robot.state.__dict__ if robot else {"error":"no robot"}

@app.get("/state")
def get_state():
    return state()

@app.get("/battery")
def battery():
    robot=get_robot()
    if not robot:
        return {"error":"no robot"}
    return {
        "level":robot.battery.get_level(),
        "charging":robot.battery.is_charging()
    }

@app.post("/move/forward")
def forward():
    print("[API] POST forward")
    actions.move_forward()
    return state()

@app.post("/move/backward")
def backward():
    print("[API] POST backward")
    actions.move_backward()
    return state()

@app.post("/move/left")
def left():
    print("[API] POST left")
    actions.turn_left()
    return state()

@app.post("/move/right")
def right():
    print("[API] POST right")
    actions.turn_right()
    return state()

@app.post("/move/stop")
def stop():
    print("[API] POST stop")
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

@app.post("/speak/{text}")
def speak(text:str):
    actions.speak(text)
    return {"message":text}


# Shell screen

@app.post("/shell/{mode}")
def shell(mode:str):
    print(f"[API] POST shell {mode}")
    actions.shell_mode(mode)
    return state()


@app.post("/shell/event/{event}")
def shell_event(event:str):
    print(f"[API] POST shell event {event}")
    actions.shell_event(event)
    return state()