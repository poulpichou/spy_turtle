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

        if self.robot:
            self.robot.state.shell_mode=mode
            self.robot.state.shell_event=None

        self.show_mode()

    def trigger(self,event,duration=5):
        print(f"[Shell] event:{event}")

        self.previous_mode=self.mode
        self.event=event
        self.event_end=time.time()+duration

        if self.robot:
            self.robot.state.shell_event=event

        self.show_event()

    def update(self):
        if self.event and time.time()>self.event_end:
            print("[Shell] event finished")

            self.event=None
            self.mode=self.previous_mode

            if self.robot:
                self.robot.state.shell_event=None
                self.robot.state.shell_mode=self.mode

            self.show_mode()

    def show_mode(self):
        modes={
            "rocket":"turtle_rocket.png",
            "happy":"turtle_happy.png",
            "walking":"turtle_walking.png",
            "sleep":"sleep.gif",
            "leds":"leds.gif",
            "fire":"fire.gif",
            "smoke":"smoke.gif"
        }

        if self.mode=="status":
            self.screen.text("SPY TURTLE",[
                "Online",
                f"Battery:{self.robot.state.battery if self.robot else '--'}%",
                "Mode:idle"
            ])

        elif self.mode=="log":
            self.show_log()

        elif self.mode in modes:
            self.show_asset(modes[self.mode])

        else:
            print(f"[Shell] unknown mode:{self.mode}")
            self.screen.text("ERROR",[self.mode])

    def show_event(self):
        events={
            "smoke":"smoke.gif",
            "fire":"fire.gif",
            "rocket":"rocket.gif",
            "dance":"dance.gif",
            "countdown":"countdown.gif"
        }

        if self.event in events:
            self.show_asset(events[self.event])

    def show_asset(self,name):
        path=self.assets/name

        print(f"[Shell] display:{path}")

        if not path.exists():
            print("[Shell] missing asset")
            return

        if path.suffix==".gif":
            self.screen.animation(path,10)
        else:
            self.screen.image(path)

    def show_log(self):
        try:
            logs=subprocess.check_output(
                "dmesg | tail -50",
                shell=True,
                text=True
            )
            lines=logs.splitlines()[-4:]
        except:
            lines=["No logs"]

        self.screen.text("LOG",lines)