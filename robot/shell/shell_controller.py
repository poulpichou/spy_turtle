from robot.shell.shell_modes import ShellMode
from robot.utils.logger import log


class ShellController:
    def __init__(self,robot=None):
        self.robot=robot
        self.mode=ShellMode.STATUS
        self.message=""
        self.message_color=(255,255,255)
        self.log_lines=[]

    def set_robot(self,robot):
        self.robot=robot

    def set_mode(self,mode):
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
        self.mode=ShellMode.STATUS
        self.update()

    def add_log(self,text):
        self.log_lines.append(text)
        self.log_lines=self.log_lines[-10:]

        if self.mode==ShellMode.LOG:
            self.update()

    def update(self):
        if not self.robot or not self.robot.shell_screen:
            return

        if self.mode==ShellMode.STATUS:
            self.show_status()
        elif self.mode==ShellMode.MESSAGE:
            self.show_message()
        elif self.mode==ShellMode.LOG:
            self.show_log()

    def show_status(self):
        self.robot.shell_screen.status(
            self.robot.state.__dict__
        )

    def show_message(self):
        self.robot.shell_screen.message(
            self.message,
            self.message_color
        )

    def show_log(self):
        self.robot.shell_screen.log(
            self.log_lines
        )