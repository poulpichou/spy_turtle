from robot.hardware.display.display import Display
from robot.utils.logger import log
from pathlib import Path
from PIL import Image
import time

class ShellScreenST7796:
    def __init__(self):
        self.display=Display()
        self.display.start()
        self.current_animation=None
        self.animation_frames=[]
        self.animation_index=0
        self.animation_time=0

    def image(self,file,rotation=0,resize=True):
        path=Path("robot/assets")/file
        if not path.exists():
            log.warn(f"[SHELL SCREEN] missing {path}")
            return
        if path.suffix.lower()==".gif":
            self.animation(str(path),rotation,resize)
        else:
            self.show_image(str(path),rotation,resize)

    def show_image(self,path,rotation=0,resize=True):
        self.stop_animation()
        image=Image.open(path).convert("RGB")
        self.display.buffer=self.prepare_image(image,rotation,resize)
        self.display.show()

    def animation(self,path,rotation=0,resize=True):
        gif=Image.open(path)
        self.animation_frames=[]
        for i in range(gif.n_frames):
            gif.seek(i)
            self.animation_frames.append(self.prepare_image(gif.convert("RGB"),rotation,resize))
        self.animation_index=0
        self.animation_time=time.time()
        self.animation_fps=10
        self.current_animation=path
        self.show_animation_frame()

    def update(self):
        if not self.current_animation:return
        if time.time()-self.animation_time<1/self.animation_fps:return
        self.animation_time=time.time()
        self.animation_index=(self.animation_index+1)%len(self.animation_frames)
        self.show_animation_frame()

    def show_animation_frame(self):
        self.display.buffer=self.animation_frames[self.animation_index]
        self.display.show()

    def prepare_image(self,image,rotation,resize):
        if rotation:image=image.rotate(rotation,expand=True)

        if resize:
            image.thumbnail((self.display.driver.width,self.display.driver.height))

        canvas=Image.new("RGB",(self.display.driver.width,self.display.driver.height),(0,0,0))
        x=(canvas.width-image.width)//2
        y=(canvas.height-image.height)//2
        canvas.paste(image,(x,y))
        return canvas

    def stop_animation(self):
        self.current_animation=None
        self.animation_frames=[]

    def clear(self):
        self.stop_animation()
        self.display.clear()
        self.display.show()

    def status(self,state):
        self.display.clear()
        lines=[
            "SPY TURTLE",
            "",
            f"BAT {state.get('battery','--')}%",
            f"FACE {state.get('emotion','--')}",
            f"LED {state.get('led_mode','--')}",
            f"MOVE {state.get('motion','--')}"
        ]
        y=10
        for line in lines:
            self.display.text(8,y,line,(255,255,255),True)
            y+=22
        self.display.show()

    def message(self,text,color=(255,255,255)):
        self.display.clear()
        self.display.text(8,40,"MESSAGE",(0,220,255),True)
        y=100
        for line in text.split("\n"):
            self.display.text(8,y,line,color,True)
            y+=22
        self.display.show()

    def log(self,lines):
        self.display.clear()
        y=40
        for line in lines[-10:]:
            self.display.text(8,y,line,(180,180,180),True)
            y+=22
        self.display.show()