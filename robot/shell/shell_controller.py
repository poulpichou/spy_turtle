import time,subprocess

class ShellController:
    def __init__(self,screen):
        self.screen=screen
        self.mode="status"
        self.previous_mode=None
        self.event=None
        self.event_end=0

    def set_mode(self,mode):
        self.mode=mode
        self.event=None
        self.update()

    def trigger(self,event,duration=10):
        self.previous_mode=self.mode
        self.event=event
        self.event_end=time.time()+duration
        self.update()

    def update(self):
        if self.event:
            if time.time()<self.event_end:
                self.show_event()
                return
            self.event=None
            self.mode=self.previous_mode

        self.show_mode()

    def show_mode(self):
        if self.mode=="status":
            self.screen.text("STATUS",[
                "Battery: --",
                "WiFi: OK",
                "Robot: idle"
            ])

        elif self.mode=="log":
            try:
                logs=subprocess.check_output(
                    ["dmesg","|","tail","-50"],
                    text=True
                )
            except:
                logs="No logs"

            self.screen.text("LOG",logs.splitlines()[-4:])

        elif self.mode=="image_1":
            self.screen.image("robot/assets/images/turtle_happy.png")

        elif self.mode=="image_2":
            self.screen.image("robot/assets/images/turtle_rocket.png")

        elif self.mode=="video_1":
            self.screen.text("VIDEO 1",["not implemented"])

        elif self.mode=="video_2":
            self.screen.text("VIDEO 2",["not implemented"])

    def show_event(self):
        if self.event=="smoke":
            self.screen.image("robot/assets/images/smoke.gif.gif")