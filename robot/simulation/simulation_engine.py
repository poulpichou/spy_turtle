import time
import random

class SimulationEngine:
    def __init__(self, face):
        self.face = face
        self.running = True

    def blink(self):
        self.face.set_eyes("closed")
        time.sleep(0.2)
        self.face.set_eyes("open")

    def yawn(self):
        self.face.set_eyes("sleepy")
        self.face.set_mouth("open")
        time.sleep(1)
        self.face.set_mouth("neutral")
        self.face.set_eyes("open")

    def random_expression(self):
        choices = ["happy", "sad", "surprised", "angry", "sleepy"]
        self.face.set_eyes(random.choice(choices))
        self.face.set_mouth(random.choice(["smile", "neutral", "sad"]))

    def idle_loop(self):
        actions = [self.blink, self.yawn, self.random_expression]
        print("Starting idle loop. Press Ctrl+C to stop.")
        while self.running:
            action = random.choice(actions)
            action()
            print("Performing idle action...")
            time.sleep(random.uniform(1.5, 3.0))