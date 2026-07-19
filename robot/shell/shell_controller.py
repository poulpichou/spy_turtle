from robot.shell.shell_modes import ShellMode
from robot.utils.logger import log
from pathlib import Path
import json


class ShellController:
    def __init__(self,screen=None):
        self.robot=None
        self.screen=screen

        self.mode=ShellMode.STATUS

        self.message=""
        self.message_color=(255,255,255)

        self.log_lines=[]

        self.image_name=None
        self.images=self.load_images()


    def set_robot(self,robot): self.robot=robot


    def load_images(self):
        path=Path(__file__).parent.parent/"assets"/"shell_images.json"

        try:
            return json.loads(path.read_text())
        except Exception as e:
            log.error(f"[SHELL] image config {e}")
            return {}


    def set_mode(self,mode):

        if mode in self.images:
            self.mode=ShellMode.IMAGE
            self.image_name=mode
            self.update()
            return

        try:
            self.mode=ShellMode(mode)
        except:
            log.warn(f"[SHELL] unknown mode {mode}")
            return

        log.info(f"[SHELL] mode {self.mode.value}")
        self.update()


    def send_text(self,text,color=None):

        self.mode=ShellMode.MESSAGE
        self.message=text

        if color:
            self.message_color=tuple(color)

        self.update()


    def trigger(self,event):
        log.info(f"[SHELL] event {event}")
        self.set_mode(event)


    def add_log(self,text):

        self.log_lines.append(text)
        self.log_lines=self.log_lines[-10:]

        if self.mode==ShellMode.LOG:
            self.update()


    def update(self):

        if not self.screen:
            return

        if self.mode==ShellMode.STATUS:
            self.screen.status(self.robot.state.__dict__)

        elif self.mode==ShellMode.MESSAGE:
            self.screen.message(
                self.message,
                self.message_color
            )

        elif self.mode==ShellMode.LOG:
            self.screen.log(
                self.log_lines
            )

        elif self.mode==ShellMode.IMAGE:
            self.show_image()


    def show_image(self):

        if self.image_name not in self.images:
            log.warn(f"[SHELL] missing image {self.image_name}")
            return

        cfg=self.images[self.image_name]

        self.screen.image(
            cfg["file"],
            cfg.get("rotation",0),
            cfg.get("resize",True)
        )