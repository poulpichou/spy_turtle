from robot.shell.shell_modes import ShellMode
from robot.utils.logger import log

class ShellController:
    def __init__(self,screen=None):
        self.robot=None
        self.screen=screen
        self.mode=ShellMode.STATUS
        self.message=""
        self.message_color=(255,255,255)
        self.image_name=""
        self.image_rotation=0
        self.image_resize=True
        self.log_lines=[]

    def set_robot(self,robot): self.robot=robot

    def set_mode(self,mode):
        try:self.mode=ShellMode(mode)
        except:
            log.warn(f"[SHELL] unknown mode {mode}")
            return
        log.info(f"[SHELL] mode {self.mode.value}")
        self.update()

    def send_text(self,text,color=None):
        self.mode=ShellMode.MESSAGE
        self.message=text
        if color:self.message_color=tuple(color)
        self.update()

    def show_image(self,name,rotation=0,resize=True):
        self.mode=ShellMode.IMAGE
        self.image_name=name
        self.image_rotation=rotation
        self.image_resize=resize
        self.update()

    def trigger(self,event):
        log.info(f"[SHELL] event {event}")
        self.mode=ShellMode.IMAGE
        self.image_name=event
        self.update()

    def add_log(self,text):
        self.log_lines.append(text)
        self.log_lines=self.log_lines[-8:]
        if self.mode==ShellMode.LOG:self.update()

    def update(self):
        if not self.screen or not self.robot:return
        state=self.robot.state.__dict__

        if self.mode==ShellMode.STATUS:
            self.screen.status(state)

        elif self.mode==ShellMode.MESSAGE:
            self.screen.message(state,self.message,self.message_color)

        elif self.mode==ShellMode.LOG:
            self.screen.log(state,self.log_lines)

        elif self.mode==ShellMode.IMAGE:
            self.screen.image(self.image_name,self.image_rotation,self.image_resize)