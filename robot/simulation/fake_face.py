import random

EYES = {
    "open": "o   o",
    "closed": "-   -",
    "happy": "^   ^",
    "sad": "o   o",
    "sleepy": "-   -",
    "angry": ">   <",
    "surprised": "O   O"
}

MOUTHS = {
    "neutral": "  -  ",
    "smile": " \\_/ ",
    "sad": " /_\\ ",
    "open": "  o  ",
    "sleepy": "  -  ",
}

class FakeFace:
    def __init__(self, oled):
        self.oled = oled
        self.eye_state = "open"
        self.mouth_state = "neutral"

    def set_eyes(self, state):
        self.eye_state = state
        self.render()

    def set_mouth(self, state):
        self.mouth_state = state
        self.render()

    def render(self):
        frame = [
            "              ",
            "  " + EYES[self.eye_state] + "  ",
            "     " + MOUTHS[self.mouth_state] + "     ",
            "              "
        ]
        self.oled.draw(frame)