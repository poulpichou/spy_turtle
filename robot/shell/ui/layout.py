from PIL import Image,ImageDraw,ImageFont

class ShellLayout:
    BLACK=(0,0,0)
    WHITE=(255,255,255)
    GREEN=(0,255,0)
    BLUE=(0,180,255)
    RED=(255,60,60)

    def __init__(self,width,height,font_path="/usr/share/fonts/truetype/roboto/Roboto-Regular.ttf"):
        self.width=width
        self.height=height
        try:
            self.font=ImageFont.truetype(font_path,18)
            self.small=ImageFont.truetype(font_path,12)
            self.big=ImageFont.truetype(font_path,26)
        except:
            self.font=self.small=self.big=ImageFont.load_default()

    def canvas(self):
        return Image.new("RGB",(self.width,self.height),self.BLACK)

    def draw_status(self,image,state):
        d=ImageDraw.Draw(image)
        d.rectangle([0,0,self.width,45],fill=(15,15,15))

        battery=getattr(state,"battery","--")
        emotion=getattr(state,"emotion","--")
        led=getattr(state,"led_mode","--")

        d.text((8,8),f"BAT {battery}%",font=self.small,fill=self.GREEN)
        d.text((8,25),f"WIFI OK",font=self.small,fill=self.BLUE)
        d.text((90,8),f"FACE {emotion}",font=self.small,fill=self.WHITE)
        d.text((90,25),f"LED {led}",font=self.small,fill=self.WHITE)

    def draw_title(self,image,title):
        d=ImageDraw.Draw(image)
        d.text((8,55),title,font=self.big,fill=self.WHITE)

    def draw_lines(self,image,lines,start=100):
        d=ImageDraw.Draw(image)
        y=start
        for line in lines:
            d.text((8,y),line,font=self.font,fill=self.WHITE)
            y+=24

    def draw_message(self,image,text):
        d=ImageDraw.Draw(image)
        d.text((8,60),"MESSAGE",font=self.big,fill=self.BLUE)
        y=120
        for line in text.split("\n"):
            d.text((8,y),line,font=self.font,fill=self.WHITE)
            y+=24