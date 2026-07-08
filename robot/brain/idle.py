import random
import time


class IdleBehaviour:
    def __init__(self, robot):
        self.robot = robot
        self.next_action = time.time() + self.random_delay()

    def update(self):
        now = time.time()

        if now >= self.next_action:
            self.perform_action()
            self.next_action = now + self.random_delay()

    def perform_action(self):
        action = random.choice([
            self.blink,
            self.look_around,
            self.yawn
        ])

        action()

    def random_delay(self):
        return random.uniform(3.0, 7.0)

    def blink(self):
        print("[Idle] blink")
        self.robot.face.blink()

    def look_around(self):
        print("[Idle] look around")

        direction = random.choice([
            "left",
            "right"
        ])

        if direction == "left":
            self.robot.face.look_left()
        else:
            self.robot.face.look_right()

    def yawn(self):
        print("[Idle] yawn")

        if hasattr(self.robot.face, "yawn"):
            self.robot.face.yawn()
        else:
            self.robot.face.set_expression("sleepy")