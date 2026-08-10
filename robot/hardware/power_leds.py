from robot.hardware.leds import LEDController as BaseLEDController

class LEDController(BaseLEDController):
    def __init__(self,*args,**kwargs):
        self.enabled=True
        super().__init__(*args,**kwargs)

    def set_enabled(self,enabled):
        self.enabled=bool(enabled)
        if not self.enabled:self._show([(0,0,0)]*self.count)
        else:
            self.last_frame_at=0.0
            super().update()
        return self.enabled

    def update(self,now=None):
        if not self.enabled:return False
        return super().update(now)
