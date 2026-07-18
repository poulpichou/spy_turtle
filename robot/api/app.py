from fastapi import FastAPI,Request
from fastapi.responses import Response
from pydantic import BaseModel
from robot.api import actions
from robot.system.runtime import get_robot

app=FastAPI()

class Command(BaseModel):
    type:str
    value:str

def state():
    robot=get_robot()
    return robot.state.__dict__ if robot else {"error":"no robot"}

@app.get("/state")
def get_state():
    print("[API] GET /state")
    return state()

@app.post("/command")
def command(cmd:Command,request:Request):
    print("==============================")
    print(f"[API] COMMAND FROM {request.client.host}")
    print(f"[API] type={cmd.type} value={cmd.value}")
    print("==============================")
    try:
        if cmd.type=="move":
            if cmd.value=="forward": actions.move_forward()
            elif cmd.value=="backward": actions.move_backward()
            elif cmd.value=="left": actions.turn_left()
            elif cmd.value=="right": actions.turn_right()
            elif cmd.value=="stop": actions.stop()

        elif cmd.type=="face":
            print("[API] FACE command")
            actions.set_emotion(cmd.value)

        elif cmd.type=="led":
            print("[API] LED command")
            actions.set_led(cmd.value)

        elif cmd.type=="head":
            print("[API] HEAD command")
            if cmd.value=="left": actions.look_left()
            elif cmd.value=="right": actions.look_right()
            elif cmd.value=="up": actions.look_up()
            elif cmd.value=="down": actions.look_down()
            elif cmd.value=="center": actions.camera_center()

        elif cmd.type=="shell":
            print("[API] SHELL command")
            actions.shell_mode(cmd.value)

        else:
            print(f"[API] UNKNOWN COMMAND {cmd.type}")

    except Exception as e:
        print(f"[API ERROR] {type(e).__name__}: {e}")

    return state()

@app.get("/camera/frame")
def camera_frame():
    frame=actions.camera_frame()
    return Response(content=frame,media_type="image/jpeg")

@app.post("/camera/start")
def camera_start():
    actions.camera_start()
    return state()

@app.post("/camera/stop")
def camera_stop():
    actions.camera_stop()
    return state()

@app.post("/speak/{text}")
def speak(text:str):
    actions.speak(text)
    return {"message":text}