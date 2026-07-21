from robot.shell.ui.shell_views import StatusView,LogView,TextView,GifView,media_view

class ShellController:
    def __init__(self,screen=None):
        self.robot=None
        self.screen=screen
        self.view=StatusView()

    def set_robot(self,robot): self.robot=robot

    def set_view(self,view):
        if self.view:self.view.close()
        self.view=view
        self.update()

    def show_status(self): self.set_view(StatusView())
    def show_log(self): self.set_view(LogView())
    def show_text(self,message): self.set_view(TextView(message))
    def show_image(self,path): self.set_view(media_view(path))

    def update(self):
        if not self.screen or not self.robot:return
        data=self.view.get_data(self.robot)
        self.screen.show_view(self.view,data,self.robot.state)

    def refresh_delay(self):
        if isinstance(self.view,GifView):return self.view.duration/1000
        return None

    def close(self):
        if self.view:self.view.close()