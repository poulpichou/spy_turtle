import json
from pathlib import Path
from robot.utils.logger import log

class PowerManager:
    COMPONENTS=("back_screen","eyes","shell_light")

    def __init__(self,robot,config_path=None):
        self.robot=robot
        self.path=Path(config_path) if config_path else Path.home()/".config"/"spy_turtle"/"power.json"
        self.data=self._load()
        self._apply_all()

    def _load(self):
        defaults={"idle_mode":False,"back_screen":True,"eyes":True,"shell_light":True,"microphone_sensitivity":60,"before_idle":{"back_screen":True,"eyes":True,"shell_light":True}}
        try:
            with self.path.open(encoding="utf-8") as file:loaded=json.load(file)
            defaults.update({key:value for key,value in loaded.items() if key in defaults})
            if isinstance(loaded.get("before_idle"),dict):defaults["before_idle"].update(loaded["before_idle"])
        except (FileNotFoundError,json.JSONDecodeError):pass
        return defaults

    def _save(self):
        self.path.parent.mkdir(parents=True,exist_ok=True)
        self.path.write_text(json.dumps(self.data,indent=2)+"\n",encoding="utf-8")

    @property
    def idle_mode(self): return bool(self.data["idle_mode"])

    def status(self):
        return {"idle_mode":self.idle_mode,"back_screen":bool(self.data["back_screen"]),"eyes":bool(self.data["eyes"]),"shell_light":bool(self.data["shell_light"]),"microphone_sensitivity":int(self.data["microphone_sensitivity"])}

    def set_component(self,name,enabled):
        if name not in self.COMPONENTS:raise ValueError(f"Unknown power component: {name}")
        if self.idle_mode:raise RuntimeError("Disable Idle mode before changing individual components")
        self.data[name]=bool(enabled)
        self._apply_component(name,bool(enabled))
        self._save()
        log.info(f"[POWER] {name}={'on' if enabled else 'off'}")
        return self.status()

    def set_microphone_sensitivity(self,value):
        self.data["microphone_sensitivity"]=max(0,min(100,int(value)))
        self._save()
        log.info(f"[POWER] microphone sensitivity={self.data['microphone_sensitivity']}% (display only)")
        return self.status()

    def set_idle(self,enabled):
        enabled=bool(enabled)
        if enabled==self.idle_mode:return self.status()
        if enabled:
            self.data["before_idle"]={name:bool(self.data[name]) for name in self.COMPONENTS}
            self.data["idle_mode"]=True
            for name in self.COMPONENTS:
                self.data[name]=False
                self._apply_component(name,False)
            if self.robot.motors:self.robot.motors.stop()
            if self.robot.servo:self.robot.servo.detach()
            if self.robot.camera and hasattr(self.robot.camera,"set_enabled"):self.robot.camera.set_enabled(False)
            elif self.robot.camera:self.robot.camera.stop()
            if self.robot.thermal_camera and hasattr(self.robot.thermal_camera,"set_enabled"):self.robot.thermal_camera.set_enabled(False)
            if self.robot.speaker:self.robot.speaker.stop()
            log.info("[POWER] idle mode enabled")
        else:
            self.data["idle_mode"]=False
            before=self.data.get("before_idle",{})
            for name in self.COMPONENTS:
                value=bool(before.get(name,True))
                self.data[name]=value
                self._apply_component(name,value)
            if self.robot.camera and hasattr(self.robot.camera,"set_enabled"):self.robot.camera.set_enabled(True)
            if self.robot.thermal_camera and hasattr(self.robot.thermal_camera,"set_enabled"):self.robot.thermal_camera.set_enabled(True)
            log.info("[POWER] idle mode disabled")
        self._save()
        return self.status()

    def _apply_all(self):
        idle=self.idle_mode
        for name in self.COMPONENTS:self._apply_component(name,False if idle else bool(self.data[name]))
        if self.robot.camera and hasattr(self.robot.camera,"set_enabled"):self.robot.camera.set_enabled(not idle)
        if self.robot.thermal_camera and hasattr(self.robot.thermal_camera,"set_enabled"):self.robot.thermal_camera.set_enabled(not idle)
        if idle:
            if self.robot.motors:self.robot.motors.stop()
            if self.robot.servo:self.robot.servo.detach()

    def _apply_component(self,name,enabled):
        if name=="shell_light" and self.robot.leds and hasattr(self.robot.leds,"set_enabled"):self.robot.leds.set_enabled(enabled)
        elif name=="eyes" and self.robot.face and hasattr(self.robot.face,"set_enabled"):self.robot.face.set_enabled(enabled)
        elif name=="back_screen" and self.robot.shell and hasattr(self.robot.shell,"set_enabled"):self.robot.shell.set_enabled(enabled)
