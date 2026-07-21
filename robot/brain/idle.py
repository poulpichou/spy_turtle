import random
import time
from robot.utils.logger import log

class IdleBehaviour:
    MIN_SLEEP_IDLE=120.0

    def __init__(self,robot):
        self.robot=robot
        self.next_action=time.monotonic()+self.random_delay()
        self.sleep_started_at=0.0

    def update(self):
        if self.robot.state.sleeping_until:
            self.update_sleep()
            return
        if self.robot.state.emotion!="neutral":return
        now=time.monotonic()
        if now<self.next_action:return
        self.perform_action()
        self.next_action=now+self.random_delay()

    def perform_action(self):
        actions=[self.blink,self.double_blink,self.look_around,self.yawn]
        weights=[52,10,30,7]
        if self.can_sleep():
            actions.append(self.sleep)
            weights.append(1)
        random.choices(actions,weights=weights,k=1)[0]()

    def can_sleep(self):
        state=self.robot.state
        return state.motion=="stop" and state.emotion=="neutral" and state.idle_seconds()>=self.MIN_SLEEP_IDLE and not self.robot.face.is_user_locked()

    def update_sleep(self):
        state=self.robot.state
        interrupted=state.last_interaction_at>self.sleep_started_at
        expired=time.time()>=state.sleeping_until
        if not interrupted and not expired:return
        reason="interaction" if interrupted else "timer"
        log.info(f"[IDLE] wake up ({reason})")
        state.sleeping_until=0.0
        state.emotion="neutral"
        self.robot.face.play("wake_up",force=True)
        self.next_action=time.monotonic()+self.random_delay()

    def random_delay(self): return random.uniform(2.5,6.5)
    def blink(self):
        log.info("[IDLE] blink")
        self.robot.face.play("blink")
    def double_blink(self):
        log.info("[IDLE] double blink")
        self.robot.face.play("double_blink")
    def look_around(self):
        direction=random.choice(["look_left","look_right","look_high","look_down"])
        log.info(f"[IDLE] {direction}")
        self.robot.face.play(direction)
    def yawn(self):
        log.info("[IDLE] yawn")
        self.robot.face.play("yawn")
    def sleep(self):
        duration=random.uniform(10.0,20.0)
        self.sleep_started_at=time.time()
        self.robot.state.sleeping_until=self.sleep_started_at+duration
        self.robot.state.emotion="sleeping"
        log.info(f"[IDLE] sleep for {duration:.1f}s")
        self.robot.face.play("sleeping",force=True)
