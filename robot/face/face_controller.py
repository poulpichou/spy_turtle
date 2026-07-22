import time
from robot.face.face_engine import FaceEngine
from robot.face.face_library import FaceLibrary

class FaceController:
    def __init__(self,renderer,leds=None):
        self.library=FaceLibrary()
        self.engine=FaceEngine(renderer,self.library)
        self.leds=leds
        self.manual_until=0.0
        self.manual_sequence=None

    def update(self):
        self.engine.update()
        if self.manual_until and time.time()>=self.manual_until:
            self.manual_until=0.0
            self.manual_sequence=None
            self.play("neutral",force=True)
            return True
        return False

    def play(self,sequence,hold=0.0,force=False):
        if not force and self.manual_until and time.time()<self.manual_until:return False
        played=self.engine.play(sequence,force=force)
        if not played:return False
        led=self.library.get_led(sequence)
        if led and self.leds:
            if hasattr(self.leds,"play"):self.leds.play(led)
            else:self.leds.set_mode(led)
        if hold>0:
            self.manual_sequence=sequence
            self.manual_until=time.time()+hold
        return True

    def user_event(self,sequence,duration=10.0): return self.play(sequence,hold=duration,force=True)
    def is_user_locked(self): return self.manual_until>time.time()
    def blink(self): self.play("blink")
    def look_left(self): self.play("look_left")
    def look_right(self): self.play("look_right")
    def look_up(self): self.play("look_high")
    def look_down(self): self.play("look_down")
    def neutral(self): self.play("neutral",force=True)
    def happy(self): self.user_event("happy")
    def love(self): self.user_event("love")
    def angry(self): self.user_event("angry")
    def surprised(self): self.user_event("surprised")
    def curious(self): self.user_event("curious")
    def sleepy(self): self.user_event("sleepy")
    def dizzy(self): self.user_event("dizzy")
    def thinking(self): self.user_event("thinking")
    def sleep(self): self.play("sleeping",force=True)
    def wake_up(self): self.play("wake_up",force=True)
    def yawn(self): self.play("yawn")
