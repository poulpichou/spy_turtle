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
        self.center_angle=float(config["center"])
        self.minimum=float(config["minimum"])
        self.maximum=float(config["maximum"])
        self.step=float(config["step"])
        self.speed=float(config["speed"])
        self.min_pulse=int(config.get("min_pulse_us",1000))
        self.max_pulse=int(config.get("max_pulse_us",2000))
        self.inverted=bool(config.get("inverted",False))
        self.detach_after=float(detach_after)
        self.current=self.center_angle
        self.target=self.center_angle
        self.last_update=time.monotonic()
        self.reached_at=None
        self.attached=False
        lgpio.gpio_claim_output(self.chip,self.gpio,0)
        self._write(self.current)
        log.info(f"[SERVO] {name} GPIO{self.gpio} ready")

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
            self._write(self.current)
            self.reached_at=None
            return True
        self.current=self.target
        if self.reached_at is None:self.reached_at=now
        elif self.attached and self.detach_after>=0 and now-self.reached_at>=self.detach_after:self.detach()
        return False

    def detach(self):
        lgpio.tx_servo(self.chip,self.gpio,0)
        self.attached=False

    def close(self):
        self.detach()
        try:lgpio.gpio_free(self.chip,self.gpio)
        except lgpio.error:pass

    def _write(self,angle):
        logical=-angle if self.inverted else angle
        ratio=(logical-self.minimum)/(self.maximum-self.minimum)
        ratio=max(0.0,min(1.0,ratio))
        pulse=round(self.min_pulse+ratio*(self.max_pulse-self.min_pulse))
        lgpio.tx_servo(self.chip,self.gpio,pulse,50)
        self.attached=True

    def _clamp(self,angle): return max(self.minimum,min(self.maximum,angle))

class ServoController:
    def __init__(self,config_path=None):
        path=Path(config_path) if config_path else Path(__file__).resolve().parent.parent/"config"/"servos.json"
        with path.open(encoding="utf-8") as file:config=json.load(file)
        self.chip=lgpio.gpiochip_open(0)
        detach_after=config.get("detach_after_seconds",0.8)
        self.pan=ServoAxis(self.chip,"pan",config["pan"],detach_after)
        self.tilt=ServoAxis(self.chip,"tilt",config["tilt"],detach_after)
        self.closed=False

    def update(self):
        now=time.monotonic()
        self.pan.update(now)
        self.tilt.update(now)

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
