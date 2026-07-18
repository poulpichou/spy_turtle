from robot.hardware.display.display import Display
from PIL import Image
import time

class ShellScreenST7796:
    def __init__(self):
        self.display=Display()
        self.display.start()
        self.display.driver.fill(0xf800)
        print("[ShellScreen] ST7796 ready")

    def show_image(self,path):
        print(f"[ShellScreen] image:{path}")
        self.display.clear()
        self.display.load_image(path)
        self.display.show()

    def image(self,path): self.show_image(path)

    def animation(self,path,fps=10):
        gif=Image.open(path)

        for frame in range(gif.n_frames):
            gif.seek(frame)

            self.display.buffer=gif.convert("RGB").resize(
                (self.display.driver.width,self.display.driver.height)
            )

            self.display.show()
            time.sleep(1/fps)

    def text(self,title,lines):
        self.display.clear()
        self.display.text(10,10,title)

        y=50
        for line in lines:
            self.display.text(10,y,line)
            y+=35

        self.display.show()

    def clear(self):
        self.display.clear()
        self.display.show()