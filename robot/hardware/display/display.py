from PIL import Image,ImageDraw
from robot.hardware.display.st7796 import ST7796
from robot.shell.ui.fonts import regular,bold


class Display:
    BLACK=(0,0,0)
    WHITE=(255,255,255)

    def __init__(self):
        self.driver=ST7796()
        self.buffer=Image.new(
            "RGB",
            (self.driver.width,self.driver.height),
            self.BLACK
        )
        self.draw=ImageDraw.Draw(self.buffer)

        try:
            self.font=regular(18)
            self.small_font=regular(12)
            self.big_font=bold(26)
        except Exception:
            from PIL import ImageFont
            self.font=ImageFont.load_default()
            self.small_font=self.font
            self.big_font=self.font

    def start(self):
        self.driver.init()

    def clear(self,color=BLACK):
        self.buffer=Image.new(
            "RGB",
            (self.driver.width,self.driver.height),
            color
        )
        self.draw=ImageDraw.Draw(self.buffer)

    def text(self,x,y,message,color=WHITE,small=False,big=False):
        font=self.font

        if small:
            font=self.small_font
        elif big:
            font=self.big_font

        self.draw.text(
            (x,y),
            str(message),
            font=font,
            fill=color
        )

    def rectangle(self,x,y,w,h,color=WHITE):
        self.draw.rectangle(
            [x,y,x+w,y+h],
            outline=color
        )

    def load_image(self,path):
        image=Image.open(path).convert("RGB")

        image.thumbnail(
            (self.driver.width,self.driver.height)
        )

        canvas=Image.new(
            "RGB",
            (self.driver.width,self.driver.height),
            self.BLACK
        )

        x=(self.driver.width-image.width)//2
        y=(self.driver.height-image.height)//2

        canvas.paste(image,(x,y))

        self.buffer=canvas
        self.draw=ImageDraw.Draw(self.buffer)

    def show(self):
        pixels=[]

        for r,g,b in self.buffer.getdata():
            value=((r&0xf8)<<8)|((g&0xfc)<<3)|(b>>3)
            pixels.extend(
                [value>>8,value&0xff]
            )

        self.driver.set_window(
            0,
            0,
            self.driver.width-1,
            self.driver.height-1
        )

        self.driver.push_pixels(pixels)

    def close(self):
        self.driver.close()