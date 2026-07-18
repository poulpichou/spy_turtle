from robot.hardware.display.display import Display

class ShellScreenST7796:
    def __init__(self):
        self.display=Display()
        self.display.start()
        print("[ShellScreen] ST7796 ready")

    def show_image(self,path):
        print(f"[ShellScreen] show_image {path}")
        self.display.clear()
        self.display.load_image(path)
        self.display.show()

    def image(self,path):
        self.show_image(path)

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