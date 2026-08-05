import time
from robot.system.state import TurtleState

class Robot:
    BATTERY_UPDATE_INTERVAL=2.0

    def __init__(self,motors,face,leds,camera,battery,speaker,servo,shell=None):
        self.motors=motors
        self.face=face
        self.leds=leds
        self.camera=camera
        self.battery=battery
        self.speaker=speaker
        self.servo=servo
        self.shell=shell
        self.state=TurtleState()
        self.brain=None
        self._last_battery_update=0.0
        self._update_battery(force=True)
        if self.face:self.face.play('neutral')
        print('[Robot] initialized')

    def update(self):
        self._update_battery()
        if self.brain:self.brain.update()
        if self.servo:self.servo.update()
        if self.leds:self.leds.update()
        if self.face and self.face.update():
            self.state.emotion='neutral'
            self.state.face_event_until=0.0
        if self.shell:
            self.shell.update()
            if hasattr(self.shell.screen,'update'):self.shell.screen.update()

    @staticmethod
    def _battery_status(level,charging):
        if charging:return 'charging'
        if level is None:return 'unknown'
        if level<=5:return 'critical'
        if level<=20:return 'low'
        if level<=50:return 'medium'
        if level<95:return 'high'
        return 'full'

    def _update_battery(self,force=False):
        now=time.monotonic()
        if not force and now-self._last_battery_update<self.BATTERY_UPDATE_INTERVAL:return
        self._last_battery_update=now
        if not self.battery:
            self.state.battery={**self.state.battery,'error':'Battery component unavailable','updated_at':None}
            return
        try:
            level=float(self.battery.get_level())
            voltage=float(self.battery.get_voltage())
            current=float(self.battery.get_current())
            charging=bool(self.battery.is_charging())
            self.state.battery={
                'level':round(level,1),'status':self._battery_status(level,charging),'voltage_v':round(voltage,3),
                'current_a':round(current,3),'power_w':round(voltage*current,3),'cells_mv':list(self.battery.get_cells()),
                'remaining_capacity':self.battery.get_remaining_capacity(),'charging':charging,
                'usb_connected':bool(self.battery.usb_connected()),'updated_at':time.time(),'error':None
            }
        except Exception as error:
            self.state.battery={'level':None,'status':'unknown','voltage_v':None,'current_a':None,'power_w':None,'cells_mv':[],'remaining_capacity':None,'charging':None,'usb_connected':None,'updated_at':None,'error':str(error)}
            print(f'[Battery] update failed: {error}')

    def forward(self): self.motors.forward()
    def backward(self): self.motors.backward()
    def turn_left(self): self.motors.left()
    def turn_right(self): self.motors.right()
    def stop(self): self.motors.stop()

    def set_emotion(self,emotion):
        self.state.emotion=emotion
        if self.face:self.face.play(emotion)

    def shell_mode(self,mode):
        if self.shell:self.shell.set_mode(mode)

    def shell_event(self,event):
        if self.shell:self.shell.trigger(event)
