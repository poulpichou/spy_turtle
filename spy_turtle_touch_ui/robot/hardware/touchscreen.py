import time
import lgpio
from smbus2 import SMBus,i2c_msg
from robot.config import settings
from robot.utils.logger import log

class Touchscreen:
    FT_ADDRESS=0x38
    GT_ADDRESSES=(0x5D,0x14)

    def __init__(self,bus=None):
        self.bus=SMBus(settings.ST7796_CTP_I2C_BUS) if bus is None else bus
        self.gpio=lgpio.gpiochip_open(0)
        self.rst=settings.ST7796_CTP_RST_GPIO
        self.int_pin=settings.ST7796_CTP_INT_GPIO
        self.controller=None
        self.address=None
        self.product=None
        self._pressed=False
        lgpio.gpio_claim_output(self.gpio,self.rst)
        try:lgpio.gpio_claim_input(self.gpio,self.int_pin)
        except Exception:pass
        self._reset()
        self._detect()
        if self.available:log.info(f"[TOUCH] ready controller={self.controller} address=0x{self.address:02X} product={self.product or '-'}")
        else:log.warn("[TOUCH] no supported capacitive controller detected (tried FT6x36 0x38, GT911 0x5D/0x14)")

    @property
    def available(self): return self.controller is not None

    def _reset(self):
        lgpio.gpio_write(self.gpio,self.rst,0);time.sleep(0.05)
        lgpio.gpio_write(self.gpio,self.rst,1);time.sleep(0.15)

    def _detect(self):
        try:
            chip=self.bus.read_byte_data(self.FT_ADDRESS,0xA8)
            self.controller="ft6x36";self.address=self.FT_ADDRESS;self.product=f"0x{chip:02X}"
            return
        except Exception:pass
        for address in self.GT_ADDRESSES:
            try:
                raw=self._gt_read(address,0x8140,4)
                product=bytes(raw).decode("ascii","ignore").strip("\x00") or "GT911"
                self.controller="gt911";self.address=address;self.product=product
                return
            except Exception:pass

    def _gt_read(self,address,register,length):
        write=i2c_msg.write(address,[(register>>8)&0xFF,register&0xFF]);read=i2c_msg.read(address,length)
        self.bus.i2c_rdwr(write,read)
        return list(read)

    def _gt_write(self,address,register,values):
        msg=i2c_msg.write(address,[(register>>8)&0xFF,register&0xFF,*values])
        self.bus.i2c_rdwr(msg)

    def _raw_point(self):
        if self.controller=="ft6x36":
            count=self.bus.read_byte_data(self.address,0x02)&0x0F
            if not count:return None
            data=self.bus.read_i2c_block_data(self.address,0x03,4)
            x=((data[0]&0x0F)<<8)|data[1];y=((data[2]&0x0F)<<8)|data[3]
            return x,y
        if self.controller=="gt911":
            status=self._gt_read(self.address,0x814E,1)[0]
            count=status&0x0F
            if not (status&0x80) or count==0:return None
            data=self._gt_read(self.address,0x8150,8)
            self._gt_write(self.address,0x814E,[0])
            x=data[1]|(data[2]<<8);y=data[3]|(data[4]<<8)
            return x,y
        return None

    def _transform(self,x,y):
        width,height=settings.ST7796_CTP_WIDTH,settings.ST7796_CTP_HEIGHT
        if settings.ST7796_CTP_SWAP_XY:x,y=y,x
        if settings.ST7796_CTP_INVERT_X:x=(width-1)-x
        if settings.ST7796_CTP_INVERT_Y:y=(height-1)-y
        return max(0,min(width-1,int(x))),max(0,min(height-1,int(y)))

    def poll(self):
        if not self.available:return None
        try:point=self._raw_point()
        except Exception as error:
            log.warn(f"[TOUCH] read failed: {error}")
            return None
        if point is None:
            self._pressed=False
            return None
        if self._pressed:return None
        self._pressed=True
        x,y=self._transform(*point)
        log.info(f"[TOUCH] x={x} y={y}")
        return x,y

    def status(self):
        return {"available":self.available,"controller":self.controller,"address":None if self.address is None else f"0x{self.address:02X}","product":self.product}

    def close(self):
        try:self.bus.close()
        except Exception:pass
        try:lgpio.gpiochip_close(self.gpio)
        except Exception:pass
