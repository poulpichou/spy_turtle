from robot.hardware.display.display import Display
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
        print("[ShellScreen] ST7796 ready")

    def show_image(self,path):
        print(f"[ShellScreen] image:{path}")
        self.stop_animation()
        self.display.clear()
        self.display.load_image(path)
        self.display.show()

    def image(self,path): self.show_image(path)

    def animation(self,path,fps=10):
        print(f"[ShellScreen] animation:{path}")

        gif=Image.open(path)

        self.animation_frames=[]

        for i in range(gif.n_frames):
            gif.seek(i)
            self.animation_frames.append(
                gif.convert("RGB").resize(
                    (self.display.driver.width,self.display.driver.height)
                )
            )

        self.animation_index=0
        self.animation_time=time.time()
        self.animation_fps=fps
        self.current_animation=path

        self.show_animation_frame()

    def update(self):
        if not self.current_animation:
            return

        if time.time()-self.animation_time < 1/self.animation_fps:
            return

        self.animation_time=time.time()
        self.animation_index+=1

        if self.animation_index>=len(self.animation_frames):
            self.animation_index=0

        self.show_animation_frame()

    def show_animation_frame(self):
        self.display.buffer=self.animation_frames[self.animation_index]
        self.display.show()

    def stop_animation(self):
        self.current_animation=None
        self.animation_frames=[]

    def text(self,title,lines):
        print(f"[ShellScreen] text:{title}")

        self.stop_animation()

        self.display.clear()
        self.display.text(10,10,title)

        y=50

        for line in lines:
            self.display.text(10,y,line)
            y+=35

        self.display.show()

    def clear(self):
        self.stop_animation()
        self.display.clear()
        self.display.show()