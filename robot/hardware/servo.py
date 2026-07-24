import json
import time
from pathlib import Path
import lgpio
from robot.utils.logger import log

class ServoAxis:
    def __init__(self,chip,name,config,detach_after):
        self.chip=chip
        self.name=name
        self.gpio=int(config["gpio"])
        self.center_angle=float(config.get("center",0.0))
        self.minimum=float(config["minimum"])
        self.maximum=float(config["maximum"])
        self.step=float(config["step"])
        self.speed=float(config["speed"])
        self.center_pulse=int(config.get("center_pulse_us",1500))
        self.microseconds_per_degree=float(config.get("microseconds_per_degree",8.0))
        self.minimum_pulse=int(config.get("minimum_pulse_us",1000))
        self.maximum_pulse=int(config.get("maximum_pulse_us",2000))
        self.inverted=bool(config.get("inverted",False))
        self.detach_after=float(detach_after)
        self.write_interval=float(config.get("write_interval_seconds",0.02))
        self.minimum_pulse_change=int(config.get("minimum_pulse_change_us",4))
        self.current=self.center_angle
        self.target=self.center_angle
        self.last_update=time.monotonic()
        self.last_write=0.0
        self.last_pulse=None
        self.reached_at=None
        self.attached=False
        lgpio.gpio_claim_output(self.chip,self.gpio,0)
        log.info(
            f"[SERVO] {name} GPIO{self.gpio} ready detached "
            f"center={self.center_angle:.1f} pulse={self.center_pulse}"
        )

    def set_target(self,angle):
        self.target=self._clamp(float(angle))
        self.reached_at=None
        return self.target

    def move(self,delta): return self.set_target(self.target+float(delta))
    def center(self): return self.set_target(self.center_angle)

    def update(self,now=None):
        now=time.monotonic() if now is None else now
        elapsed=max(0.0,now-self.last_update)
        self.last_update=now
        difference=self.target-self.current
        if abs(difference)>0.05:
            distance=min(abs(difference),self.speed*elapsed)
            self.current+=distance if difference>0 else -distance
            self._write(self.current,now)
            self.reached_at=None
            return True
        self.current=self.target
        if self.reached_at is None:
            self._write(self.current,now,force=True)
            self.reached_at=now
        elif self.attached and self.detach_after>=0 and now-self.reached_at>=self.detach_after:
            self.detach()
        return False

    def status(self):
        return {
            "current":round(self.current,1),
            "target":round(self.target,1),
            "center":round(self.center_angle,1),
            "minimum":round(self.minimum,1),
            "maximum":round(self.maximum,1),
            "pulse_us":self.last_pulse,
            "attached":self.attached
        }

    def detach(self):
        if self.attached:lgpio.tx_servo(self.chip,self.gpio,0)
        self.attached=False
        self.last_pulse=None

    def close(self):
        self.detach()
        try:lgpio.gpio_free(self.chip,self.gpio)
        except lgpio.error:pass

    def _write(self,angle,now=None,force=False):
        now=time.monotonic() if now is None else now
        if not force and now-self.last_write<self.write_interval:return False
        offset=angle-self.center_angle
        if self.inverted:offset=-offset
        pulse=round(self.center_pulse+offset*self.microseconds_per_degree)
        pulse=max(self.minimum_pulse,min(self.maximum_pulse,pulse))
        if not force and self.last_pulse is not None and abs(pulse-self.last_pulse)<self.minimum_pulse_change:
            return False
        lgpio.tx_servo(self.chip,self.gpio,pulse,50)
        self.last_pulse=pulse
        self.last_write=now
        self.attached=True
        log.debug(f"[SERVO] {self.name} angle={angle:.1f} pulse={pulse}")
        return True

    def _clamp(self,angle): return max(self.minimum,min(self.maximum,angle))

class ServoController:
    def __init__(self,config_path=None):
        path=Path(config_path) if config_path else Path(__file__).resolve().parent.parent/"config"/"servos.json"
        with path.open(encoding="utf-8") as file:config=json.load(file)
        self.chip=lgpio.gpiochip_open(0)
        detach_after=config.get("detach_after_seconds",0.25)
        self.pan=ServoAxis(self.chip,"pan",config["pan"],detach_after)
        self.tilt=ServoAxis(self.chip,"tilt",config["tilt"],detach_after)
        self.closed=False

    def update(self):
        now=time.monotonic()
        self.pan.update(now)
        self.tilt.update(now)

    def status(self): return {"pan":self.pan.status(),"tilt":self.tilt.status()}

    def look_left(self):
        angle=self.pan.move(-self.pan.step)
        log.info(f"[SERVO] pan target {angle:.1f}")

    def look_right(self):
        angle=self.pan.move(self.pan.step)
        log.info(f"[SERVO] pan target {angle:.1f}")

    def look_up(self):
        angle=self.tilt.move(-self.tilt.step)
        log.info(f"[SERVO] tilt target {angle:.1f}")

    def look_down(self):
        angle=self.tilt.move(self.tilt.step)
        log.info(f"[SERVO] tilt target {angle:.1f}")

    def center(self):
        self.pan.center()
        self.tilt.center()
        log.info("[SERVO] center")

    def detach(self):
        self.pan.detach()
        self.tilt.detach()

    def close(self):
        if self.closed:return
        self.pan.close()
        self.tilt.close()
        lgpio.gpiochip_close(self.chip)
        self.closed=True
