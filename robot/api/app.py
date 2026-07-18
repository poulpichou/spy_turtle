from fastapi import FastAPI
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from pathlib import Path

from robot.api import actions
from robot.system.runtime import get_robot


app = FastAPI()


class Command(BaseModel):
    type:str
    value:str


def state():
    robot=get_robot()

    if robot:
        return robot.state.__dict__

    return {"error":"no robot"}



@app.get("/state")
def get_state():
    print("[API] GET /state")
    return state()



@app.post("/command")
def command(cmd:Command):

    print(f"[API] COMMAND {cmd.type} {cmd.value}")

    try:

        if cmd.type=="move":

            if cmd.value=="forward":
                actions.move_forward()

            elif cmd.value=="backward":
                actions.move_backward()

            elif cmd.value=="left":
                actions.turn_left()

            elif cmd.value=="right":
                actions.turn_right()

            elif cmd.value=="stop":
                actions.stop()


        elif cmd.type=="face":
            actions.set_emotion(cmd.value)


        elif cmd.type=="led":
            actions.set_led(cmd.value)


        elif cmd.type=="shell":
            actions.shell_mode(cmd.value)


        elif cmd.type=="head":

            if cmd.value=="left":
                actions.look_left()

            elif cmd.value=="right":
                actions.look_right()

            elif cmd.value=="up":
                actions.look_up()

            elif cmd.value=="down":
                actions.look_down()

            elif cmd.value=="center":
                actions.camera_center()


    except Exception as e:
        print("[API ERROR]",e)


    return state()



@app.get("/camera/frame")
def camera_frame():

    print("[API] camera frame")

    return Response(
        content=actions.camera_frame(),
        media_type="image/jpeg"
    )



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

    return {
        "message":text
    }



# IMPORTANT:
# Le frontend doit être monté EN DERNIER

FRONTEND=Path(__file__).parent.parent.parent/"frontend"

app.mount(
    "/",
    StaticFiles(directory=FRONTEND,html=True),
    name="frontend"
)