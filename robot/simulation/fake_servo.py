class FakeServo:
    def __init__(self):
        self.pan=0.0
        self.tilt=0.0
        self.pan_step=10.0
        self.tilt_step=8.0
        print("[FakeServo] ready")

    def update(self): pass

    def look_left(self):
        self.pan=max(-60.0,self.pan-self.pan_step)
        print(f"[FakeServo] pan:{self.pan}")

    def look_right(self):
        self.pan=min(60.0,self.pan+self.pan_step)
        print(f"[FakeServo] pan:{self.pan}")

    def look_up(self):
        self.tilt=max(-30.0,self.tilt-self.tilt_step)
        print(f"[FakeServo] tilt:{self.tilt}")

    def look_down(self):
        self.tilt=min(35.0,self.tilt+self.tilt_step)
        print(f"[FakeServo] tilt:{self.tilt}")

    def center(self):
        self.pan=0.0
        self.tilt=0.0
        print("[FakeServo] center")

    def detach(self): pass
    def close(self): pass
