from robot.shell.shell_controller import ShellController as BaseShellController

class ShellController(BaseShellController):
    def __init__(self,*args,**kwargs):
        self.enabled=True
        super().__init__(*args,**kwargs)

    def set_enabled(self,enabled):
        self.enabled=bool(enabled)
        if not self.screen:return self.enabled
        if not self.enabled:
            self.screen.display.clear((0,0,0))
            self.screen.display.show()
        else:self.update()
        return self.enabled

    def update(self):
        if not self.enabled:return
        return super().update()
