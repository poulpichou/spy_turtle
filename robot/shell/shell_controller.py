import time
from robot.shell.shell_modes import ShellMode

class ShellController:
    def __init__(self,screen):
        self.screen=screen
        self.mode=ShellMode.STATUS
        self.previous=None
        self.event_until=0

    def set_mode(self,mode):
        self.mode=mode
        self.previous=None
        self.update()

    def update(self):
        if self.event_until and time.time()>self.event_until:
            self.mode=self.previous
            self.previous=None
            self.event_until=0

        if self.mode==ShellMode.IMAGE_1:
            self.screen.show_image("robot/assets/images/turtle_happy.png")
        elif self.mode==ShellMode.IMAGE_2:
            self.screen.show_image("robot/assets/images/turtle_rocket.png")
        elif self.mode==ShellMode.LOG:
            self.show_log()
        elif self.mode==ShellMode.STATUS:
            self.show_status()
        elif self.mode==ShellMode.VIDEO_1:
            self.screen.show_image("robot/assets/images/smoke.gif.gif")
        elif self.mode==ShellMode.VIDEO_2:
            self.screen.show_image("robot/assets/images/turtle_walking.png")

    def show_status(self):
        self.screen.show_text("SPY TURTLE",[
            "Battery: -- %",
            "WiFi: OK",
            "CPU: -- C",
            "Mode: "+self.mode.value
        ])

    def show_log(self):
        import subprocess
        log=subprocess.getoutput("dmesg | tail -5")
        self.screen.show_text("SYSTEM LOG",log.split("\n"))

    def event(self,mode,duration=10):
        self.previous=self.mode
        self.mode=mode
        self.event_until=time.time()+duration
        self.update()