from fastapi import FastAPI
from fastapi.responses import Response
from pydantic import BaseModel
from robot.system.runtime import get_robot
from robot.api import actions

app=FastAPI()


class Command(BaseModel):
    type:str
    value:str


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


@app.post("/command")
def command(cmd:Command):
    print(f"[API] command {cmd.type}:{cmd.value}")

    if cmd.type=="move":
        if cmd.value=="forward": actions.move_forward()
        elif cmd.value=="backward": actions.move_backward()
        elif cmd.value=="left": actions.turn_left()
        elif cmd.value=="right": actions.turn_right()
        elif cmd.value=="stop": actions.stop()

    elif cmd.type=="face":
        actions.set_emotion(cmd.value)

    elif cmd.type=="led":
        actions.set_led(cmd.value)

    elif cmd.type=="head":
        if cmd.value=="left": actions.look_left()
        elif cmd.value=="right": actions.look_right()
        elif cmd.value=="up": actions.look_up()
        elif cmd.value=="down": actions.look_down()
        elif cmd.value=="center": actions.camera_center()

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
    frame=actions.camera_frame()
    return Response(content=frame,media_type="image/jpeg")


@app.post("/speak/{text}")
def speak(text:str):
    actions.speak(text)
    return {"message":text}