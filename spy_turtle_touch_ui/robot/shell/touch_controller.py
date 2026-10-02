import subprocess
from robot.api import actions
from robot.shell.ui.touch_views import HomeView,CommandsView,SelectionView,AdminView,WifiView,ConfirmShutdownView
from robot.system.wifi import wifi_manager
from robot.utils.logger import log

class TouchController:
    def __init__(self,robot,shell,touchscreen):
        self.robot=robot
        self.shell=shell
        self.touchscreen=touchscreen

    def update(self):
        point=self.touchscreen.poll()
        if point is None:return
        x,y=point
        if self.robot.power.idle_mode:
            self.robot.power.set_idle(False)
            self.open_home()
            return
        view=self.shell.view
        if not getattr(view,"interactive",False):
            self.open_home()
            return
        action=view.action_at(x,y)
        if action is not None:self._dispatch(action,view)

    def open_home(self):
        self.shell.expires_at=0.0
        self.shell.active_mode="touch_home"
        self.shell.set_view(HomeView())
        self.robot.state.shell_mode="touch_home"

    def _dispatch(self,action,view):
        log.info(f"[TOUCH UI] action={action}")
        if action=="status":self.shell.show_status(reset_effects=False);return
        if action=="logs":self.shell.show_log();return
        if action=="commands":self._show(CommandsView(),"touch_commands");return
        if action=="admin":self._show(AdminView(),"touch_admin");return
        if action=="idle":
            self.robot.power.set_idle(not self.robot.power.idle_mode)
            if not self.robot.power.idle_mode:self.open_home()
            return
        if action=="back":
            if isinstance(view,(CommandsView,AdminView)):self.open_home()
            elif isinstance(view,SelectionView):self._show(CommandsView(),"touch_commands")
            elif isinstance(view,WifiView):self._show(AdminView(),"touch_admin")
            else:self.open_home()
            return
        if action=="prev":
            view.page=max(0,view.page-1);self.shell.update();return
        if action=="next":
            view.page+=1;self.shell.update();return
        if action in ("faces","leds","shell","audio"):
            self._show(SelectionView(action),f"touch_{action}");return
        if isinstance(action,tuple) and action[0]=="select":
            self._select(view.section,action[1]);return
        if action=="volume_down":self._volume(-10);return
        if action=="volume_up":self._volume(10);return
        if action=="wifi":self._show(WifiView(),"touch_wifi");return
        if isinstance(action,tuple) and action[0]=="wifi":
            wifi_manager.connect(action[1]);self._show(WifiView(view.page),"touch_wifi");return
        if action=="shutdown":self._show(ConfirmShutdownView(),"touch_shutdown_confirm");return
        if action=="cancel":self._show(AdminView(),"touch_admin");return
        if action=="confirm":
            log.warn("[TOUCH UI] shutdown requested")
            subprocess.Popen(["sudo","-n","shutdown","now"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
            return

    def _show(self,view,mode):
        self.shell.expires_at=0.0
        self.shell.active_mode=mode
        self.shell.set_view(view)
        self.robot.state.shell_mode=mode

    def _select(self,section,name):
        if section=="faces":actions.set_emotion(name)
        elif section=="leds":actions.set_led(name)
        elif section=="shell":actions.shell_show(name)
        elif section=="audio":actions.speak(name)
        if section!="shell":self._show(SelectionView(section),"touch_"+section)

    def _volume(self,delta):
        if not self.robot.speaker:return
        current=int(getattr(self.robot.speaker,"volume",60))
        self.robot.speaker.set_volume(max(0,min(100,current+delta)))
        self._show(AdminView(),"touch_admin")
