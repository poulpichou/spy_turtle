import json
import time
from collections import deque
from pathlib import Path
from threading import RLock
import lgpio
from robot.config import settings
from robot.utils.logger import log

class ServoAxis:
    def __init__(self,chip,name,gpio,config,detach_after,safe_pulse_min=1000,safe_pulse_max=2000):
        self.chip=chip;self.name=name;self.gpio=int(gpio)
        self.center_angle=float(config.get('center_angle_deg',config.get('center',0.0)))
        self.minimum=float(config.get('minimum_angle_deg',config.get('minimum',-90.0)))
        self.maximum=float(config.get('maximum_angle_deg',config.get('maximum',90.0)))
        self.step=float(config.get('step_deg',config.get('step',5.0)))
        self.speed=float(config.get('speed_deg_per_second',config.get('speed',50.0)))
        self.center_pulse=int(config.get('center_pulse_us',1500))
        self.microseconds_per_degree=float(config.get('microseconds_per_degree',8.0))
        self.minimum_pulse=int(safe_pulse_min);self.maximum_pulse=int(safe_pulse_max)
        self.inverted=bool(config.get('inverted',False));self.detach_after=float(detach_after)
        self.write_interval=float(config.get('write_interval_seconds',0.02))
        self.minimum_pulse_change=int(config.get('minimum_pulse_change_us',4))
        self.current=self.center_angle;self.target=self.center_angle
        self.last_update=time.monotonic();self.last_write=0.0;self.last_pulse=None;self.reached_at=None;self.attached=False
        self.write_count=0;self.detach_count=0;self.error_count=0;self.last_error=None
        self.last_tx_result=None;self.last_tx_busy=None;self.last_tx_at=None;self.events=deque(maxlen=80)
        lgpio.gpio_claim_output(self.chip,self.gpio,0)
        log.info(f'[SERVO] {name} GPIO{self.gpio} ready center={self.center_angle:.1f}deg pulse={self.center_pulse}us range={self.minimum:.0f}..{self.maximum:.0f}deg')

    def _event(self,action,**fields):
        event={'at':round(time.time(),3),'action':action,**fields};self.events.append(event)
        log.info(f'[SERVO DIAG] {self.name} {event}')

    def set_target(self,angle):
        self.target=self._clamp(float(angle));self.reached_at=None;return self.target
    def move(self,delta):return self.set_target(self.target+float(delta))
    def center(self):return self.set_target(self.center_angle)

    def update(self,now=None):
        now=time.monotonic() if now is None else now
        elapsed=max(0.0,now-self.last_update);self.last_update=now
        difference=self.target-self.current
        if abs(difference)>0.05:
            distance=min(abs(difference),self.speed*elapsed);self.current+=distance if difference>0 else -distance
            self._write(self.current,now);self.reached_at=None;return True
        self.current=self.target
        if self.reached_at is None:
            self._write(self.current,now,force=True);self.reached_at=now
        elif self.attached and self.detach_after>=0 and now-self.reached_at>=self.detach_after:self.detach()
        return False

    def status(self):
        return {'current':round(self.current,1),'target':round(self.target,1),'center':round(self.center_angle,1),
                'minimum':round(self.minimum,1),'maximum':round(self.maximum,1),'pulse_us':self.last_pulse,
                'center_pulse_us':self.center_pulse,'microseconds_per_degree':self.microseconds_per_degree,'attached':self.attached}

    def diagnostic(self):
        now=time.monotonic()
        return {**self.status(),'gpio':self.gpio,'write_count':self.write_count,'detach_count':self.detach_count,
                'error_count':self.error_count,'last_error':self.last_error,'last_tx_result':self.last_tx_result,
                'last_tx_busy':self.last_tx_busy,'last_tx_age_s':round(now-self.last_tx_at,3) if self.last_tx_at else None,
                'last_update_age_s':round(now-self.last_update,3),'events':list(self.events)}

    def detach(self):
        if not self.attached:return
        try:
            result=lgpio.tx_servo(self.chip,self.gpio,0)
            self.detach_count+=1;self._event('detach',result=result)
        except Exception as error:
            self.error_count+=1;self.last_error=str(error);self._event('detach_error',error=str(error));raise
        finally:self.attached=False;self.last_pulse=None;self.last_tx_busy=None

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
        if not force and self.last_pulse is not None and abs(pulse-self.last_pulse)<self.minimum_pulse_change:return False
        try:
            result=lgpio.tx_servo(self.chip,self.gpio,pulse,50)
            busy=lgpio.tx_busy(self.chip,self.gpio,lgpio.TX_PWM)
        except Exception as error:
            self.error_count+=1;self.last_error=str(error);self._event('write_error',pulse_us=pulse,error=str(error));raise
        self.last_pulse=pulse;self.last_write=now;self.attached=True;self.write_count+=1
        self.last_tx_result=result;self.last_tx_busy=busy;self.last_tx_at=now
        if self.write_count==1 or self.write_count%50==0 or busy!=1:self._event('write',pulse_us=pulse,result=result,busy=busy,count=self.write_count)
        return True

    def _clamp(self,angle):return max(self.minimum,min(self.maximum,angle))

class ServoController:
    def __init__(self,config_path=None):
        path=Path(config_path) if config_path else Path(__file__).resolve().parent.parent/'config'/'servos.json'
        with path.open(encoding='utf-8') as file:config=json.load(file)
        self._lock=RLock();self.chip=lgpio.gpiochip_open(0);detach_after=config.get('detach_after_seconds',0.25)
        safe_min=config.get('safe_pulse_min_us',1000);safe_max=config.get('safe_pulse_max_us',2000)
        self.pan=ServoAxis(self.chip,'pan',settings.SERVO_PAN_PIN,config['pan'],detach_after,safe_min,safe_max)
        self.tilt=ServoAxis(self.chip,'tilt',settings.SERVO_TILT_PIN,config['tilt'],detach_after,safe_min,safe_max)
        self.closed=False;self.update_count=0;self.last_controller_update=None;self.reset_count=0

    def update(self):
        with self._lock:
            now=time.monotonic();self.update_count+=1;self.last_controller_update=now
            self.pan.update(now);self.tilt.update(now)

    def status(self):
        with self._lock:return {'pan':self.pan.status(),'tilt':self.tilt.status()}
    def diagnostic(self):
        with self._lock:
            return {'chip':self.chip,'closed':self.closed,'update_count':self.update_count,'reset_count':self.reset_count,
                    'update_age_s':round(time.monotonic()-self.last_controller_update,3) if self.last_controller_update else None,
                    'pan':self.pan.diagnostic(),'tilt':self.tilt.diagnostic()}
    def look_left(self):
        with self._lock:log.info(f'[SERVO] pan target {self.pan.move(-self.pan.step):.1f}deg')
    def look_right(self):
        with self._lock:log.info(f'[SERVO] pan target {self.pan.move(self.pan.step):.1f}deg')
    def look_up(self):
        with self._lock:log.info(f'[SERVO] tilt target {self.tilt.move(-self.tilt.step):.1f}deg')
    def look_down(self):
        with self._lock:log.info(f'[SERVO] tilt target {self.tilt.move(self.tilt.step):.1f}deg')
    def center(self):
        with self._lock:self.pan.center();self.tilt.center();log.info('[SERVO] center')
    def detach(self):
        with self._lock:self.pan.detach();self.tilt.detach()

    def reset_gpio(self):
        with self._lock:
            if self.closed:raise RuntimeError('Servo controller is closed')
            log.info('[SERVO DIAG] GPIO reset start')
            for axis in (self.pan,self.tilt):axis.close()
            lgpio.gpiochip_close(self.chip)
            self.closed=True
            new_chip=lgpio.gpiochip_open(0)
            try:
                lgpio.gpio_claim_output(new_chip,self.pan.gpio,0)
                lgpio.gpio_claim_output(new_chip,self.tilt.gpio,0)
            except Exception:
                lgpio.gpiochip_close(new_chip)
                raise
            self.chip=new_chip;self.closed=False;self.reset_count+=1
            now=time.monotonic()
            for axis in (self.pan,self.tilt):
                axis.chip=new_chip;axis.attached=False;axis.last_pulse=None;axis.last_write=0.0
                axis.last_update=now;axis.reached_at=now;axis.last_tx_busy=None
                axis._event('gpio_reset',reset_count=self.reset_count)
            log.info('[SERVO DIAG] GPIO reset successful; outputs idle, send a new head command')
            return self.diagnostic()

    def close(self):
        with self._lock:
            if self.closed:return
            self.pan.close();self.tilt.close();lgpio.gpiochip_close(self.chip);self.closed=True
