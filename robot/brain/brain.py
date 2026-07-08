import random
import time


class Brain:
    def __init__(self, robot):
        self.robot = robot
        self.last_action = time.time()

    def update(self):
        now = time.time()

        if now - self.last_action > 3:
            self.idle_behaviour()
            self.last_action = now

    def idle_behaviour(self):
        action = random.choice([
            self.blink,
            self.look_around
        ])

        action()

    def blink(self):
        print("[Brain] blink")
        self.robot.face.blink()

    def look_around(self):
        print("[Brain] looking around")
        self.robot.face.look_left()