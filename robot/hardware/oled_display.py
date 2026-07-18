from luma.core.interface.serial import i2c
from luma.oled.device import ssd1306
from PIL import Image

class OLEDDisplay:
    def __init__(self,address,name="oled"):
        self.name=name
        self.device=ssd1306(i2c(port=1,address=address))
        self.image=Image.new("1",(128,64))
        print(f"[OLEDDisplay] {name} ready at {hex(address)}")

    def show(self,bitmap):
        image=Image.new("1",(128,64))
        pixels=image.load()
        for y,line in enumerate(bitmap):
            for x,value in enumerate(line):
                if value!=".":
                    pixels[x,y]=255
        self.device.display(image)

    def clear(self): self.device.clear()