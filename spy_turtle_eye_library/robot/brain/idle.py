import random
import time
from robot.utils.logger import log

class IdleBehaviour:
    def __init__(self,robot):
        self.robot=robot
        self.next_action=time.monotonic()+self.random_delay()

    def update(self):
        now=time.monotonic()
        if now<self.next_action:return
        self.perform_action()
        self.next_action=now+self.random_delay()

    def perform_action(self):
        action=random.choices(
            [self.blink,self.double_blink,self.look_around,self.yawn],
            weights=[55,10,30,5],
            k=1
        )[0]
        action()

    def random_delay(self): return random.uniform(2.5,6.5)

    def blink(self):
        log.info("[IDLE] blink")
        self.robot.face.play("blink")

    def double_blink(self):
        log.info("[IDLE] double blink")
        self.robot.face.play("double_blink")

    def look_around(self):
        direction=random.choice(["look_left","look_right"])
        log.info(f"[IDLE] {direction}")
        self.robot.face.play(direction)

    def yawn(self):
        log.info("[IDLE] yawn")
        self.robot.face.play("yawn")
