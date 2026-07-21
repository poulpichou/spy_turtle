from robot.shell.ui.shell_views import StatusView,LogView
from robot.utils.logger import log

class ShellController:
    def __init__(self,screen=None):
        self.robot=None
        self.screen=screen
        self.view=StatusView()
        self.data={}

    def set_robot(self,robot): self.robot=robot

    def show_status(self):
        self.view=StatusView()
        self.update()

    def show_log(self):
        self.view=LogView()
        self.update()

    def update(self):
        if not self.screen or not self.robot:return

        if isinstance(self.view,StatusView):
            self.data=self.robot.state.__dict__

        elif isinstance(self.view,LogView):
            self.data=log.tail(20)

        self.screen.show_view(self.view,self.data,self.robot.state)