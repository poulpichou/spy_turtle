from fastapi import FastAPI
from software.api.state import STATE
from software.api import actions

app = FastAPI()

@app.get("/state")
def get_state():
    return STATE.__dict__

@app.post("/move/forward")
def forward():
    actions.move_forward()
    return STATE.__dict__

@app.post("/move/backward")
def backward():
    actions.move_backward()
    return STATE.__dict__

@app.post("/move/left")
def left():
    actions.turn_left()
    return STATE.__dict__

@app.post("/move/right")
def right():
    actions.turn_right()
    return STATE.__dict__

@app.post("/emotion/{emotion}")
def emotion(emotion: str):
    actions.set_emotion(emotion)
    return STATE.__dict__

@app.post("/led/{mode}")
def led(mode: str):
    actions.set_led(mode)
    return STATE.__dict__