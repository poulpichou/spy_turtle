from smbus2 import SMBus

class UPSHat:
    ADDRESS=0x2d

    def __init__(self):
        self.bus=SMBus(1)

    def read(self,reg): return self.bus.read_byte_data(self.ADDRESS,reg)

    def read16(self,reg): return self.read(reg)|(self.read(reg+1)<<8)

    def battery(self,index):
        return self.read16(0x30+index*2)

    def batteries(self):
        return [self.battery(i) for i in range(4)]

    def voltage(self):
        cells=self.batteries()
        return sum(cells)/1000

    def charging(self): return bool(self.read(0x02)&0x80)

    def usb_present(self): return bool(self.read(0x02)&0x20)

    def fast_charge(self): return bool(self.read(0x02)&0x40)