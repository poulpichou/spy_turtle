from smbus2 import SMBus
from robot.utils.logger import log

class UPSHat:
    ADDRESS=0x2d

    def __init__(self):
        self.bus=SMBus(1)

    def read(self,reg):
        try:
            value=self.bus.read_byte_data(self.ADDRESS,reg)
            log.debug(f'[BATTERY I2C] addr=0x{self.ADDRESS:02X} reg=0x{reg:02X} value=0x{value:02X}')
            return value
        except OSError as error:
            log.debug(f'[BATTERY I2C] addr=0x{self.ADDRESS:02X} reg=0x{reg:02X} failed: {error}')
            raise
    def read16(self,reg): return self.read(reg)|(self.read(reg+1)<<8)

    def battery(self,index): return self.read16(0x30+index*2)
    def batteries(self): return [self.battery(i) for i in range(4)]

    def voltage(self): return self.read16(0x20)/1000
    def current(self):
        value=self.read16(0x22)
        if value>=32768: value-=65536
        return value

    def percentage(self): return self.read16(0x24)
    def remaining_capacity(self): return self.read16(0x26)
    def remaining_discharge(self): return self.read16(0x28)
    def remaining_charge(self): return self.read16(0x2a)

    def charging(self): return bool(self.read(0x02)&0x80)
    def fast_charge(self): return bool(self.read(0x02)&0x40)
    def usb_present(self): return bool(self.read(0x02)&0x20)