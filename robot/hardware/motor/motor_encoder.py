from math import pi
from threading import Lock
import lgpio

class MotorEncoder:
    def __init__(self,pin_a,pin_b=None,name="motor",inverted=False,pull_up=True,pulses_per_rev=0,wheel_diameter_mm=0):
        self.name=name;self.inverted=bool(inverted)
        self.pulses_per_rev=int(pulses_per_rev);self.wheel_diameter_mm=float(wheel_diameter_mm)
        self.pin_a=int(pin_a);self.pin_b=int(pin_b) if pin_b is not None else None
        self.lock=Lock();self.ticks=0;self.state=None;self.closed=False
        self.chip=None;self.callbacks=[];self.claimed=[];self.edges=0;self.alert_errors=0
        flags=lgpio.SET_PULL_UP if pull_up else lgpio.SET_PULL_DOWN
        try:
            self.chip=lgpio.gpiochip_open(0)
            for pin in (self.pin_a,self.pin_b):
                if pin is None:continue
                lgpio.gpio_claim_alert(self.chip,pin,lgpio.BOTH_EDGES,flags)
                self.claimed.append(pin)
            if self.pin_b is not None:self.state=self._state()
            for pin in self.claimed:self.callbacks.append(lgpio.callback(self.chip,pin,lgpio.BOTH_EDGES,self._changed))
        except Exception:
            self.close()
            raise

    def _state(self):
        return (int(lgpio.gpio_read(self.chip,self.pin_a))<<1)|int(lgpio.gpio_read(self.chip,self.pin_b))

    def _changed(self,chip,gpio,level,tick):
        if self.closed or level not in (0,1):return
        try:
            with self.lock:
                self.edges+=1
                if self.pin_b is None:
                    if level==1:self.ticks+=-1 if self.inverted else 1
                    return
                state=self._state()
                transitions={(0,1):1,(1,3):1,(3,2):1,(2,0):1,(1,0):-1,(3,1):-1,(2,3):-1,(0,2):-1}
                delta=transitions.get((self.state,state),0)
                self.state=state
                if self.inverted:delta=-delta
                self.ticks+=delta
        except Exception:
            with self.lock:self.alert_errors+=1

    def get_ticks(self):
        with self.lock:return self.ticks

    def reset(self):
        with self.lock:self.ticks=0

    def status(self):
        with self.lock:ticks=self.ticks;edges=self.edges;errors=self.alert_errors
        revolutions=ticks/self.pulses_per_rev if self.pulses_per_rev>0 else None
        distance=revolutions*pi*self.wheel_diameter_mm if revolutions is not None and self.wheel_diameter_mm>0 else None
        return {"ticks":ticks,"revolutions":round(revolutions,4) if revolutions is not None else None,
                "distance_mm":round(distance,1) if distance is not None else None,"quadrature":self.pin_b is not None,
                "backend":"lgpio_alert","edges":edges,"alert_errors":errors}

    def close(self):
        self.closed=True
        for cb in self.callbacks:
            try:cb.cancel()
            except Exception:pass
        self.callbacks.clear()
        if self.chip is not None:
            for pin in self.claimed:
                try:lgpio.gpio_free(self.chip,pin)
                except Exception:pass
            self.claimed.clear()
            try:lgpio.gpiochip_close(self.chip)
            except Exception:pass
            self.chip=None
