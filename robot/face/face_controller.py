from robot.face.face_engine import FaceEngine
from robot.face.face_library import FaceLibrary

class FaceController:
    def __init__(self, renderer):
        library = FaceLibrary()
        self.engine = FaceEngine(renderer, library)

    def update(self):
        self.engine.update()

    def play(self, sequence):
        self.engine.play(sequence)

    def blink(self):
        self.play("blink")

    def look_left(self):
        self.play("look_left")

    def look_right(self):
        self.play("look_right")

    def look_up(self):
        self.play("look_up")

    def look_down(self):
        self.play("look_down")

    def neutral(self):
        self.play("neutral")

    def happy(self):
        self.play("happy")

    def sad(self):
        self.play("sad")

    def angry(self):
        self.play("angry")

    def surprised(self):
        self.play("surprised")

    def sleepy(self):
        self.play("sleepy")

    def sleep(self):
        self.play("sleep")

    def wake_up(self):
        self.play("wake_up")

    def yawn(self):
        self.play("yawn")

    def wink_left(self):
        self.play("wink_left")

    def wink_right(self):
        self.play("wink_right")