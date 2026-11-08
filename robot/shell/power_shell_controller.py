from robot.shell.shell_controller import ShellController as BaseShellController

class ShellController(BaseShellController):
    def __init__(self,*args,**kwargs):
        self.enabled=True
        super().__init__(*args,**kwargs)

    def set_enabled(self,enabled):
        from robot.shell.diagnostics import trace
        with self.screen.lock if self.screen else _NoLock():
            trace('power_request',requested=bool(enabled),current=self.enabled,mode=self.active_mode,view=type(self.view).__name__)
            was_enabled=self.enabled
            self.enabled=bool(enabled)
            if not self.screen:
                trace('blocked',reason='no_screen',enabled=self.enabled)
                return self.enabled
            if not self.enabled:
                self.screen.display.clear((0,0,0))
                self.screen.show()
            else:
                if not was_enabled:
                    try:
                        trace('screen_reinit_start',reason='idle_wakeup')
                        self.screen.display.start()
                        trace('screen_reinit',reason='idle_wakeup',success=True)
                    except Exception as error:
                        trace('errors',operation='screen_reinit',error=repr(error))
                        raise
                self.update()
                trace('screen_wakeup_drawn',mode=self.active_mode,view=type(self.view).__name__)
            trace('power_done',enabled=self.enabled,mode=self.active_mode,view=type(self.view).__name__)
            return self.enabled

    def update(self):
        if not self.enabled:return
        return super().update()

class _NoLock:
    def __enter__(self):return self
    def __exit__(self,*args):return False
