from PIL import Image, ImageDraw, ImageFont
from robot.hardware.display.st7796 import ST7796

class Display:
    BLACK=(0,0,0)
    WHITE=(255,255,255)
    RED=(255,0,0)
    GREEN=(0,255,0)
    BLUE=(0,0,255)

    def __init__(self):
        self.driver=ST7796()
        self.buffer=Image.new("RGB",(self.driver.width,self.driver.height),self.BLACK)
        self.draw=ImageDraw.Draw(self.buffer)
        try:
            self.font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",32)
        except:
            self.font=ImageFont.load_default()

    def start(self):
        self.driver.init()

    def clear(self,color=BLACK):
        self.buffer=Image.new("RGB",(self.driver.width,self.driver.height),color)
        self.draw=ImageDraw.Draw(self.buffer)

    def text(self,x,y,message,color=WHITE):
        self.draw.text((x,y),message,font=self.font,fill=color)

    def rectangle(self,x,y,w,h,color=WHITE):
        self.draw.rectangle([x,y,x+w,y+h],outline=color)

    def load_image(self,path):
        self.buffer=Image.open(path).convert("RGB").resize((self.driver.width,self.driver.height))
        self.draw=ImageDraw.Draw(self.buffer)

    def show(self):
        pixels=[]
        for r,g,b in self.buffer.getdata():
            value=((r&0xf8)<<8)|((g&0xfc)<<3)|(b>>3)
            pixels.extend([value>>8,value&0xff])
        self.driver.set_window(0,0,self.driver.width-1,self.driver.height-1)
        self.driver.push_pixels(pixels)

    def close(self):
        self.driver.close()
