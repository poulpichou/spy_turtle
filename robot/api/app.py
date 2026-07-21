from pathlib import Path
from fastapi import FastAPI,HTTPException
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel,Field
from robot.api import actions
from robot.assets.assets import get_assets
from robot.system.runtime import get_robot
from robot.utils.logger import log

app=FastAPI()

class Command(BaseModel):
    type:str
    value:str=""
    extra:dict=Field(default_factory=dict)

def state():
    robot=get_robot()
    return robot.state.to_dict() if robot else {"error":"no robot"}

@app.get("/state")
def get_state(): return state()

@app.get("/assets")
def get_available_assets(): return {section:build_assets(section) for section in ("shell","eyes","leds","audio")}

def build_assets(section):
    return [{"name":name,"label":asset.get("label",name)} for name,asset in get_assets(section).items() if asset.get("available",True)]

@app.post("/command")
def command(cmd:Command):
    log.info(f"[API] command {cmd.type} {cmd.value}")
    try:
        if cmd.type=="move":
            if cmd.value=="forward":actions.move_forward()
            elif cmd.value=="backward":actions.move_backward()
            elif cmd.value=="left":actions.turn_left()
            elif cmd.value=="right":actions.turn_right()
            elif cmd.value=="stop":actions.stop()
            else:raise ValueError(f"Unknown movement: {cmd.value}")
        elif cmd.type=="face":actions.set_emotion(cmd.value)
        elif cmd.type=="led":actions.set_led(cmd.value)
        elif cmd.type=="shell":actions.shell_show(cmd.value)
        elif cmd.type=="shell_text":actions.shell_text(cmd.value)
        elif cmd.type=="head":
            if cmd.value=="left":actions.look_left()
            elif cmd.value=="right":actions.look_right()
            elif cmd.value=="up":actions.look_up()
            elif cmd.value=="down":actions.look_down()
            elif cmd.value=="center":actions.camera_center()
            else:raise ValueError(f"Unknown head command: {cmd.value}")
        elif cmd.type=="sound":actions.speak(cmd.value)
        else:raise ValueError(f"Unknown command type: {cmd.type}")
    except Exception as error:
        log.error(f"[API ERROR] {error}")
        raise HTTPException(status_code=400,detail=str(error)) from error
    return state()

@app.get("/camera/frame")
def camera_frame(): return Response(content=actions.camera_frame(),media_type="image/jpeg")

@app.post("/camera/start")
def camera_start():
    actions.camera_start()
    return state()

@app.post("/camera/stop")
def camera_stop():
    actions.camera_stop()
    return state()

FRONTEND=Path(__file__).parent.parent.parent/"frontend"
app.mount("/",StaticFiles(directory=FRONTEND,html=True),name="frontend")
