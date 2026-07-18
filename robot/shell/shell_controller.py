from pathlib import Path
import time,subprocess

class ShellController:
    def __init__(self,screen,robot=None):
        self.screen=screen
        self.robot=robot
        self.assets=Path(__file__).parent.parent/"assets"/"images"
        self.mode="status"
        self.previous_mode="status"
        self.event=None
        self.event_end=0

    def set_robot(self,robot): self.robot=robot

    def set_mode(self,mode):
        print(f"[Shell] mode:{mode}")
        self.event=None
        self.mode=mode
        self.show_mode()

    def trigger(self,event,duration=5):
        print(f"[Shell] event:{event}")
        self.previous_mode=self.mode
        self.event=event
        self.event_end=time.time()+duration
        self.show_event()

    def update(self):
        if self.event and time.time()>self.event_end:
            self.event=None
            self.mode=self.previous_mode
            self.show_mode()

    def show_mode(self):

        modes={
            "rocket":"turtle_rocket.png",
            "walking":"turtle_walking.png",
            "happy":"turtle_happy.png",
            "sleep":"sleep.gif",
            "leds":"leds.gif",
            "fire":"fire.gif",
            "smoke":"smoke.gif"
        }

        if self.mode=="status":
            self.show_status()
        elif self.mode=="log":
            self.show_log()
        elif self.mode in modes:
            path=self.assets/modes[self.mode]
            if path.suffix==".gif": self.screen.animation(path,10)
            else: self.screen.image(path)

    def show_status(self):

        state=self.robot.state if self.robot else None

        battery=getattr(state,"battery","--")
        emotion=getattr(state,"emotion","--")
        led=getattr(state,"led_mode","--")
        motion=getattr(state,"motion","--")
        camera="ON" if self.robot and self.robot.camera else "OFF"

        lines=[
            "SPY TURTLE",
            "",
            f"🔋 Battery {battery}%",
            "📡 WiFi OK",
            f"🙂 Face {emotion}",
            f"💡 LEDs {led}",
            f"🐢 Move {motion}",
            f"📷 Cam {camera}",
            "SYSTEM READY"
        ]

        self.screen.text("STATUS",lines)

    def show_event(self):

        events={
            "smoke":"smoke.gif",
            "fire":"fire.gif",
            "rocket":"rocket.gif",
            "dance":"dance.gif",
            "countdown":"countdown.gif"
        }

        if self.event in events:
            path=self.assets/events[self.event]
            if path.suffix==".gif": self.screen.animation(path,10)
            else: self.screen.image(path)

    def show_log(self):

        lines=self.get_logs()

        self.screen.text(
            "LOG",
            lines
        )

    def get_logs(self):

        files=[
            Path("/home/spy/spy_turtle/logs/spy_turtle.log"),
            Path("logs/spy_turtle.log")
        ]

        for f in files:
            if f.exists():
                return f.read_text().splitlines()[-10:]

        try:
            out=subprocess.check_output(
                ["journalctl","-n","10","--no-pager"],
                text=True
            )
            return out.splitlines()[-10:]
        except:
            return ["No logs"]