from fastapi import FastAPI

from robot.factory.robot_factory import RobotFactory

from robot.api import actions


app = FastAPI()


robot = RobotFactory.create(
    simulation=True
)


@app.get("/state")
def get_state():
    return robot.state.__dict__


@app.post("/move/forward")
def forward():
    actions.move_forward(robot)
    return robot.state.__dict__


@app.post("/move/backward")
def backward():
    actions.move_backward(robot)
    return robot.state.__dict__


@app.post("/move/left")
def left():
    actions.turn_left(robot)
    return robot.state.__dict__


@app.post("/move/right")
def right():
    actions.turn_right(robot)
    return robot.state.__dict__


@app.post("/move/stop")
def stop():
    actions.stop(robot)
    return robot.state.__dict__


@app.post("/emotion/{emotion}")
def emotion(emotion: str):

    actions.set_emotion(
        robot,
        emotion
    )

    return robot.state.__dict__


@app.post("/led/{mode}")
def led(mode: str):

    actions.set_led(
        robot,
        mode
    )

    return robot.state.__dict__