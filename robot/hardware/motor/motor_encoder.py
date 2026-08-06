from math import pi
from threading import Lock

from gpiozero import DigitalInputDevice

class MotorEncoder:
    TRANSITIONS={(0,1):1,(1,3):1,(3,2):1,(2,0):1,(1,0):-1,(3,1):-1,(2,3):-1,(0,2):-1}

    def __init__(self,pin_a,pin_b,name,inverted=False,pull_up=True,pulses_per_rev=0,wheel_diameter_mm=0):
        self.name=name
        self.inverted=inverted
        self.pulses_per_rev=int(pulses_per_rev)
        self.wheel_diameter_mm=float(wheel_diameter_mm)
        self.a=DigitalInputDevice(pin_a,pull_up=pull_up)
        self.b=DigitalInputDevice(pin_b,pull_up=pull_up)
        self.lock=Lock()
        self.ticks=0
        self.state=self._state()
        self.a.when_activated=self._changed
        self.a.when_deactivated=self._changed
        self.b.when_activated=self._changed
        self.b.when_deactivated=self._changed

    def _state(self):return (int(self.a.value)<<1)|int(self.b.value)

    def _changed(self):
        state=self._state()
        delta=self.TRANSITIONS.get((self.state,state),0)
        self.state=state
        if self.inverted:delta=-delta
        if delta:
            with self.lock:self.ticks+=delta

    def reset(self):
        with self.lock:self.ticks=0

    def status(self):
        with self.lock:ticks=self.ticks
        revolutions=ticks/self.pulses_per_rev if self.pulses_per_rev>0 else None
        distance=revolutions*pi*self.wheel_diameter_mm if revolutions is not None and self.wheel_diameter_mm>0 else None
        return {"ticks":ticks,"revolutions":round(revolutions,4) if revolutions is not None else None,"distance_mm":round(distance,1) if distance is not None else None}

    def close(self):
        self.a.close()
        self.b.close()
