from robot.hardware.ups_hat import UPSHat
from robot.utils.logger import log

class Battery:
    def __init__(self):
        self.ups=UPSHat()
        log.info("[BATTERY] ready")

    def get_level(self): return self.ups.percentage()
    def get_voltage(self): return self.ups.voltage()
    def get_current(self): return self.ups.current()
    def get_cells(self): return self.ups.batteries()
    def get_remaining_capacity(self): return self.ups.remaining_capacity()
    def is_charging(self): return self.ups.charging()
    def usb_connected(self): return self.ups.usb_present()