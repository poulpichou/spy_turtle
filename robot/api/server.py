from fastapi import FastAPI
from robot.system.runtime import get_robot
from robot.api import actions

app = FastAPI()

@app.get("/state")
def get_state():
    print("[API] GET state")
    robot = get_robot()
    return robot.state.__dict__ if robot else {"error": "no robot"}

@app.post("/move/forward")
def forward():
    print("[API] POST forward")
    actions.move_forward()
    robot = get_robot()
    return robot.state.__dict__ if robot else {"error": "no robot"}

@app.post("/move/backward")
def backward():
    print("[API] POST backward")
    actions.move_backward()
    robot = get_robot()
    return robot.state.__dict__ if robot else {"error": "no robot"}

@app.post("/move/left")
def left():
    print("[API] POST left")
    actions.turn_left()
    robot = get_robot()
    return robot.state.__dict__ if robot else {"error": "no robot"}

@app.post("/move/right")
def right():
    print("[API] POST right")
    actions.turn_right()
    robot = get_robot()
    return robot.state.__dict__ if robot else {"error": "no robot"}

@app.post("/move/stop")
def stop():
    print("[API] POST stop")
    actions.stop()
    robot = get_robot()
    return robot.state.__dict__ if robot else {"error": "no robot"}