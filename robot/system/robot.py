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
        if self.face:self.face.play("neutral")
        print("[Robot] initialized")

    def update(self):
        self._update_battery()
        if self.brain:self.brain.update()
        if self.servo:self.servo.update()
        if self.leds:self.leds.update()
        if self.face and self.face.update():
            self.state.emotion="neutral"
            self.state.face_event_until=0.0
        if self.shell:
            self.shell.update()
            if hasattr(self.shell.screen,"update"):self.shell.screen.update()

    def _update_battery(self,force=False):
        now=time.monotonic()
        if not force and now-self._last_battery_update<self.BATTERY_UPDATE_INTERVAL:return
        self._last_battery_update=now
        if not self.battery:
            self.state.battery_error="Battery component unavailable"
            return
        try:
            self.state.battery=float(self.battery.get_level())
            self.state.battery_voltage=float(self.battery.get_voltage())
            self.state.battery_current=float(self.battery.get_current())
            self.state.battery_cells=list(self.battery.get_cells())
            self.state.battery_charging=bool(self.battery.is_charging())
            self.state.battery_usb=bool(self.battery.usb_connected())
            self.state.battery_updated_at=time.time()
            self.state.battery_error=None
        except Exception as error:
            self.state.battery=None
            self.state.battery_voltage=None
            self.state.battery_current=None
            self.state.battery_cells=[]
            self.state.battery_charging=None
            self.state.battery_usb=None
            self.state.battery_updated_at=None
            self.state.battery_error=str(error)
            print(f"[Battery] update failed: {error}")

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