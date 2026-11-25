class FakeServo:
    def __init__(self):
        self.pan=0.0
        self.tilt=0.0
        self.pan_step=10.0
        self.tilt_step=6.0
        print("[FakeServo] ready")

    def update(self): pass
    def status(self):
        return {
            "pan":{"current":self.pan,"target":self.pan,"center":0.0,"minimum":-90.0,"maximum":90.0,"attached":False},
            "tilt":{"current":self.tilt,"target":self.tilt,"center":0.0,"minimum":-15.0,"maximum":22.0,"attached":False}
        }

    def look_left(self):
        self.pan=max(-90.0,self.pan-self.pan_step)
        print(f"[FakeServo] pan:{self.pan}")

    def look_right(self):
        self.pan=min(90.0,self.pan+self.pan_step)
        print(f"[FakeServo] pan:{self.pan}")

    def look_up(self):
        self.tilt=max(-15.0,self.tilt-self.tilt_step)
        print(f"[FakeServo] tilt:{self.tilt}")

    def look_down(self):
        self.tilt=min(22.0,self.tilt+self.tilt_step)
        print(f"[FakeServo] tilt:{self.tilt}")

    def center(self):
        self.pan=getattr(self,"pan_center_offset",0.0)
        self.tilt=0.0
        print("[FakeServo] center")

    def set_position(self,pan,tilt):
        self.pan=max(-90.0,min(90.0,float(pan)))
        self.tilt=max(-60.0,min(60.0,float(tilt)))
        print(f'[FakeServo] position pan:{self.pan} tilt:{self.tilt}')

    def road(self):self.pan=getattr(self,'pan_center_offset',0.0);self.tilt=30.0
    def get_pan_center_offset(self):return getattr(self,'pan_center_offset',0.0)
    def set_pan_center_offset(self,value):
        self.pan_center_offset=max(-20.0,min(20.0,float(value)));self.pan=self.pan_center_offset
        return self.pan_center_offset
    def detach(self): pass
    def close(self): pass
