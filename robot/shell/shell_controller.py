import json
import time
from pathlib import Path
from robot.assets.assets import get_asset
from robot.shell.ui.shell_views import StatusView,LogView,TextView,GifView,media_view
from robot.utils.logger import log

class ShellController:
    def __init__(self,screen=None,config_path=None):
        self.robot=None
        self.screen=screen
        self.view=StatusView()
        path=Path(config_path) if config_path else Path(__file__).resolve().parent.parent/"config"/"shell_modes.json"
        with path.open(encoding="utf-8") as file:self.config=json.load(file)
        self.expires_at=0.0
        self.active_mode="status"

    def set_robot(self,robot): self.robot=robot

    def set_view(self,view):
        if self.view:self.view.close()
        self.view=view
        self.update()

    def show_status(self,reset_effects=True):
        self.expires_at=0.0
        self.active_mode="status"
        self.set_view(StatusView())
        if self.robot:
            self.robot.state.shell_mode="status"
            if reset_effects:self._restore_default_effects()

    def show_log(self):
        self.expires_at=0.0
        self.active_mode="log"
        self.set_view(LogView())
        if self.robot:self.robot.state.shell_mode="log"

    def show_text(self,message):
        self.expires_at=0.0
        self.active_mode="text"
        self.set_view(TextView(message))
        if self.robot:self.robot.state.shell_mode="text"

    def show_image(self,name):
        asset=get_asset("shell",name)
        self.active_mode=name
        self.set_view(media_view(asset["path"],asset.get("label")))
        if self.robot:self.robot.state.shell_mode=name
        self._start_mode(name)

    def show_default(self):
        asset=get_asset("shell")
        self.set_view(media_view(asset["path"],asset.get("label")))

    def _start_mode(self,name):
        profile=self.config.get("modes",{}).get(name,{})
        duration=float(profile.get("duration_seconds",self.config.get("default_duration_seconds",60)))
        self.expires_at=time.monotonic()+duration if duration>0 else 0.0
        if not self.robot:return
        face=profile.get("face")
        if face and self.robot.face:
            self.robot.face.user_event(face,duration)
            self.robot.state.emotion=face
            self.robot.state.face_event_until=self.robot.face.manual_until
        led=profile.get("led")
        if led and self.robot.leds:
            self.robot.leds.set_mode(led)
            self.robot.state.led_mode=led
        log.info(f"[SHELL] mode {name} duration={duration:.0f}s face={face or '-'} led={led or '-'}")

    def _restore_default_effects(self):
        if not self.robot:return
        if self.robot.face:
            self.robot.face.manual_until=0.0
            self.robot.face.manual_sequence=None
            self.robot.face.play("neutral",force=True)
            self.robot.state.emotion="neutral"
            self.robot.state.face_event_until=0.0
        if self.robot.leds:
            self.robot.leds.set_mode("neutral")
            self.robot.state.led_mode="neutral"

    def update(self):
        if self.expires_at and time.monotonic()>=self.expires_at:
            log.info(f"[SHELL] mode {self.active_mode} expired")
            self.show_status()
            return
        if not self.screen or not self.robot:return
        data=self.view.get_data(self.robot)
        self.screen.show_view(self.view,data,self.robot.state)

    def refresh_delay(self):
        if isinstance(self.view,GifView):return self.view.duration/1000
        return None

    def close(self):
        if self.view:self.view.close()
