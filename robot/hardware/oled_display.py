from luma.core.interface.serial import i2c
from luma.core.error import DeviceNotFoundError
from luma.oled.device import ssd1306
from PIL import Image
from robot.utils.logger import log

class OLEDDisplay:
    def __init__(self,address,name="oled"):
        self.name=name
        self.address=address
        self.device=ssd1306(i2c(port=1,address=address))
        self.image=Image.new("1",(128,64))
        print(f"[OLEDDisplay] {name} ready at {hex(address)}")

    def show(self,bitmap):
        image=Image.new("1",(128,64))
        pixels=image.load()
        for y,line in enumerate(bitmap):
            for x,value in enumerate(line):
                if value!=".":pixels[x,y]=255
        try:self.device.display(image)
        except (DeviceNotFoundError,OSError) as exc:
            log.error(f"[OLEDDisplay] {self.name} ({self.address:#04x}) update failed: {type(exc).__name__}: {exc}")

    def clear(self):
        try:self.device.clear()
        except (DeviceNotFoundError,OSError) as exc:
            log.error(f"[OLEDDisplay] {self.name} ({self.address:#04x}) clear failed: {type(exc).__name__}: {exc}")
