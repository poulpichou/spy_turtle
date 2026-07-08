import time

class FaceAnimations:
    def __init__(self, eyes, mouth):
        self.eyes = eyes
        self.mouth = mouth

    def blink(self):
        self.eyes.closed()
        time.sleep(0.12)
        self.eyes.open()

    def double_blink(self):
        self.blink()
        time.sleep(0.15)
        self.blink()

    def yawn(self):
        self.eyes.sleepy()
        self.mouth.open()
        time.sleep(1)
        self.mouth.neutral()
        self.eyes.open()

    def look_left(self):
        self.eyes.looking_left()

    def look_right(self):
        self.eyes.looking_right()

    def wake_up(self):
        self.eyes.closed()
        time.sleep(0.3)
        self.eyes.sleepy()
        time.sleep(0.3)
        self.eyes.open()

    def sleep(self):
        self.eyes.sleepy()
        self.mouth.sleepy()