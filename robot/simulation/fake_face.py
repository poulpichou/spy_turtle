from robot.face.face import Face


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


class FakeFace(Face):
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

    def blink(self):
        self.set_eyes("closed")
        self.set_eyes("open")

    def look_left(self):
        self.set_eyes("open")
        print("[Face] looking left")

    def look_right(self):
        self.set_eyes("open")
        print("[Face] looking right")

    def set_expression(self, expression):
        if expression == "happy":
            self.set_eyes("happy")
            self.set_mouth("smile")

        elif expression == "sad":
            self.set_eyes("sad")
            self.set_mouth("sad")

        elif expression == "surprised":
            self.set_eyes("surprised")
            self.set_mouth("open")

        elif expression == "sleepy":
            self.set_eyes("sleepy")
            self.set_mouth("sleepy")

        elif expression == "angry":
            self.set_eyes("angry")
            self.set_mouth("sad")

        else:
            self.set_eyes("open")
            self.set_mouth("neutral")

    def render(self):
        frame = [
            "              ",
            "  " + EYES[self.eye_state] + "  ",
            "     " + MOUTHS[self.mouth_state] + "     ",
            "              "
        ]

        self.oled.draw(frame)

    def yawn(self):
        self.set_eyes("sleepy")
        self.set_mouth("open")

        import time
        time.sleep(0.8)

        self.set_mouth("neutral")
        self.set_eyes("open")