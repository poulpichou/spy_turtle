import time
import spidev
import lgpio

class ST7796:
    def __init__(self,dc=25,rst=24):
        self.dc=dc
        self.rst=rst
        self.width=320
        self.height=480

        self.gpio=lgpio.gpiochip_open(4)
        lgpio.gpio_claim_output(self.gpio,self.dc)
        lgpio.gpio_claim_output(self.gpio,self.rst)

        self.spi=spidev.SpiDev()
        self.spi.open(0,0)
        self.spi.max_speed_hz=16000000
        self.spi.mode=0

        lgpio.gpio_write(self.gpio,self.rst,1)

    def command(self,value):
        lgpio.gpio_write(self.gpio,self.dc,0)
        self.spi.writebytes([value])

    def data(self,values):
        lgpio.gpio_write(self.gpio,self.dc,1)
        self.spi.writebytes(values)

    def reset(self):
        lgpio.gpio_write(self.gpio,self.rst,0)
        time.sleep(0.1)
        lgpio.gpio_write(self.gpio,self.rst,1)
        time.sleep(0.2)

    def init(self):
        self.reset()

        self.command(0x01)
        time.sleep(0.15)

        self.command(0x11)
        time.sleep(0.12)

        self.command(0x3A)
        self.data([0x55])

        self.command(0x36)
        self.data([0x48])

        self.command(0x21)
        self.command(0x29)

        time.sleep(0.1)

    def set_window(self,x0,y0,x1,y1):
        self.command(0x2A)
        self.data([x0>>8,x0&0xff,x1>>8,x1&0xff])

        self.command(0x2B)
        self.data([y0>>8,y0&0xff,y1>>8,y1&0xff])

        self.command(0x2C)

    def push_pixels(self,pixels):
        for i in range(0,len(pixels),4096):
            self.data(pixels[i:i+4096])

    def fill(self,color):
        self.set_window(0,0,self.width-1,self.height-1)

        pixel=[color>>8,color&0xff]
        buffer=pixel*512
        total=self.width*self.height

        while total:
            count=min(total,512)
            self.push_pixels(buffer[:count*2])
            total-=count

    def close(self):
        self.spi.close()
        lgpio.gpiochip_close(self.gpio)