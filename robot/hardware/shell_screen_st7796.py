from robot.hardware.display.display import Display
from robot.shell.ui.shell_ui import ShellUI
from PIL import Image
import time


class ShellScreenST7796:
    def __init__(self):
        self.display=Display()
        self.display.start()
        self.ui=ShellUI(self.display)

        self.current_animation=None
        self.animation_frames=[]
        self.animation_index=0
        self.animation_time=0

    def image(self,path):
        self.stop_animation()
        self.ui.image(path)

    def animation(self,path,fps=10):
        gif=Image.open(path)

        self.animation_frames=[]

        for i in range(gif.n_frames):
            gif.seek(i)
            self.animation_frames.append(
                gif.convert("RGB")
            )

        self.animation_index=0
        self.animation_time=time.time()
        self.animation_fps=fps
        self.current_animation=True

        self.show_animation_frame()

    def update(self):
        if not self.current_animation:
            return

        if time.time()-self.animation_time < 1/self.animation_fps:
            return

        self.animation_time=time.time()
        self.animation_index=(self.animation_index+1)%len(self.animation_frames)
        self.show_animation_frame()

    def show_animation_frame(self):
        self.display.buffer=self.animation_frames[self.animation_index]
        self.display.show()

    def stop_animation(self):
        self.current_animation=None
        self.animation_frames=[]

    def status(self,state):
        self.stop_animation()
        self.ui.status(state)

    def message(self,text,color=(255,255,255)):
        self.stop_animation()
        self.ui.message(text,color)

    def log(self,lines):
        self.stop_animation()
        self.ui.log(lines)

    def clear(self):
        self.stop_animation()
        self.display.clear()
        self.display.show()