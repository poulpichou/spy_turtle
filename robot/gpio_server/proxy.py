import time
from robot.gpio_server.client import client,GPIOUnavailable
from robot.utils.logger import log

class BaseProxy:
    component=None
    def __init__(self):
        self._last_warning=0.0
        # Fail fast on startup instead of silently creating a robot without motors/servos.
        self._call('status')
    def _call(self,method,*args):
        try:return client.call(self.component,method,*args)
        except GPIOUnavailable as error:
            now=time.monotonic()
            if now-self._last_warning>2:log.error(f'[GPIO CLIENT] {self.component}.{method}: {error}');self._last_warning=now
            raise
    def close(self):pass # The server owns the GPIO. Main-process rebuild must not close it.
    def update(self):pass # Physical update loop lives in GPIO server.
    def status(self):return self._call('status')
    def diagnostic(self):return self._call('diagnostic')

class MotorProxy(BaseProxy):
    component='motors'
    def forward(self,speed=None):return self._call('forward',speed)
    def backward(self,speed=None):return self._call('backward',speed)
    def left(self,speed=None):return self._call('left',speed)
    def right(self,speed=None):return self._call('right',speed)
    def turn_left(self,speed=None):return self._call('turn_left',speed)
    def turn_right(self,speed=None):return self._call('turn_right',speed)
    def stop(self):return self._call('stop')
    def joystick(self,left,right):return self._call('joystick',left,right)
    def set_speeds(self,left,right):return self._call('set_speeds',left,right)
    def set_left_speed(self,speed):return self._call('set_left_speed',speed)
    def set_right_speed(self,speed):return self._call('set_right_speed',speed)
    def set_speed_percent(self,percent):return self._call('set_speed_percent',percent)
    def get_speed_percent(self):return self._call('get_speed_percent')
    def reset_encoders(self):return self._call('reset_encoders')
    def set_correction_enabled(self,enabled):return self._call('set_correction_enabled',bool(enabled))
    def reset_pwm(self):return self._call('reset_pwm')

class ServoProxy(BaseProxy):
    component='servo'
    def look_left(self):return self._call('look_left')
    def look_right(self):return self._call('look_right')
    def look_up(self):return self._call('look_up')
    def look_down(self):return self._call('look_down')
    def center(self):return self._call('center')
    def detach(self):return self._call('detach')
    def reset_gpio(self):return self._call('reset_gpio')
