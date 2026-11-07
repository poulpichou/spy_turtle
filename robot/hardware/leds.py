import colorsys
import json
import math
import os
import random
import struct
import time
from pathlib import Path
from robot.utils.logger import log

class LEDController:
    def __init__(self,config_path=None):
        path=Path(config_path) if config_path else Path(__file__).resolve().parent.parent/"config"/"leds.json"
        with path.open(encoding="utf-8") as file:self.config=json.load(file)
        settings=self.config["settings"]
        self.device=str(settings.get("device","/dev/leds0"))
        self.count=int(settings["count"])
        self.global_brightness=float(settings.get("brightness",1.0))
        self.user_brightness=1.0 # Additional multiplier; original animation levels unchanged.
        self.reversed=bool(settings.get("reversed",False))
        self.modes=self.config["modes"]
        self.animations=self.config["animations"]
        self.links=self.config.get("links",{})
        self.headlights_color=self._load_headlights_color()
        self.headlights_intensity=self._load_headlights_intensity()
        self.mode="off"
        self.animation_name=self.modes["off"]["animation"]
        self.started_at=time.monotonic()
        self.last_frame_at=0.0
        self.frame_interval=1/50
        self.fd=None
        self._configure_device()
        self._show([(0,0,0)]*self.count)
        log.info(f"[LED] ready device={self.device} count={self.count}")

    @staticmethod
    def _headlights_path(): return Path.home()/".config"/"spy_turtle"/"headlights.json"

    def _load_headlights_color(self):
        try:
            value=json.loads(self._headlights_path().read_text(encoding="utf-8"))["color"]
            if isinstance(value,str) and len(value)==7 and value[0]=="#":
                int(value[1:],16)
                return value.lower()
        except (OSError,ValueError,KeyError,TypeError):pass
        return "#ffffff"

    def _load_headlights_intensity(self):
        try:return max(0,min(100,int(json.loads(self._headlights_path().read_text(encoding="utf-8")).get("intensity",100))))
        except (OSError,ValueError,TypeError):return 100
    def _save_headlights(self):
        path=self._headlights_path();path.parent.mkdir(parents=True,exist_ok=True)
        tmp=path.with_suffix(".tmp");tmp.write_text(json.dumps({"color":self.headlights_color,"intensity":self.headlights_intensity})+"\n",encoding="utf-8");tmp.replace(path)
    def set_headlights_intensity(self,value):
        value=int(value)
        if not 0<=value<=100:raise ValueError("Intensity must be 0..100")
        self.headlights_intensity=value;self._save_headlights();self.last_frame_at=0.0
        return value

    def set_headlights_color(self,color):
        if not isinstance(color,str) or len(color)!=7 or not color.startswith("#"):
            raise ValueError("Color must be #RRGGBB")
        try:int(color[1:],16)
        except ValueError as error:raise ValueError("Color must be #RRGGBB") from error
        self.headlights_color=color.lower()
        self._save_headlights()
        self.last_frame_at=0.0
        log.info(f"[LIGHTS] headlights color={self.headlights_color}")
        return self.headlights_color

    def _open_device(self):
        try:return os.open(self.device,os.O_WRONLY)
        except PermissionError as error:raise RuntimeError(f"No permission to write {self.device}") from error
        except FileNotFoundError as error:raise RuntimeError(f"LED device not found: {self.device}") from error

    def _configure_device(self):
        fd=self._open_device()
        try:
            written=os.write(fd,b"\x00")
            if written!=1:raise RuntimeError("Unable to configure LED pass-through brightness")
        finally:
            os.close(fd)

    def set_mode(self,name):
        if name not in self.modes:raise ValueError(f"Unknown LED mode: {name}")
        if self.mode==name:return False # Avoid duplicate log and animation reset.
        self.mode=name
        self.animation_name=self.modes[name]["animation"]
        if self.animation_name not in self.animations:raise ValueError(f"Unknown LED animation: {self.animation_name}")
        self.started_at=time.monotonic()
        self.last_frame_at=0.0
        log.info(f"[LED] mode {name} -> {self.animation_name}")
        return True

    def play(self,name): return self.set_mode(name)
    def off(self): return self.set_mode("off")
    def rainbow(self): return self.set_mode("rainbow")
    def police(self): return self.set_mode("police")
    def fire(self): return self.set_mode("fire")
    def ocean(self): return self.set_mode("wave")

    def static(self,color):
        self.animations["_runtime_static"]={"type":"solid","color":list(color)}
        self.modes["_runtime_static"]={"label":"Static","animation":"_runtime_static"}
        return self.set_mode("_runtime_static")

    def breathing(self,color):
        self.animations["_runtime_breathing"]={"type":"breathing","color":list(color),"period":2.5}
        self.modes["_runtime_breathing"]={"label":"Breathing","animation":"_runtime_breathing"}
        return self.set_mode("_runtime_breathing")

    def linked_mode(self,group,name): return self.links.get(group,{}).get(name)

    def update(self,now=None):
        now=time.monotonic() if now is None else now
        if now-self.last_frame_at<self.frame_interval:return False
        self.last_frame_at=now
        frame,brightness=self._render(self.animations[self.animation_name],now-self.started_at)
        if self.animation_name=="headlights":self._show(self._scale(frame,self.headlights_intensity/100)) # Independent headlights intensity
        else:self._show(self._scale(frame,self.global_brightness*self.user_brightness*brightness))
        return True

    def get_brightness_percent(self): return round(self.user_brightness*100)
    def set_brightness_percent(self,value):
        value=int(value)
        if not 0<=value<=100:raise ValueError("LED brightness must be 0..100")
        self.user_brightness=value/100
        self.last_frame_at=0.0
        self.update()
        log.info(f"[LED] intensity multiplier {value}%")
        return value

    def _render(self,animation,elapsed):
        effect=animation.get("type",animation.get("effect","off"))
        brightness=float(animation.get("brightness",1.0))
        if effect=="sequence":return self._render_sequence(animation,elapsed)
        if effect=="headlights":
            start=int(animation.get("start",15));end=int(animation.get("end",26))
            color=tuple(bytes.fromhex(self.headlights_color[1:]))
            return [color if start<=i<=end else (0,0,0) for i in range(self.count)],1.0
        if effect=="off":return [(0,0,0)]*self.count,brightness
        if effect=="solid":return [self._color(animation.get("color",[255,255,255]))]*self.count,brightness
        if effect=="rainbow":
            period=max(0.05,float(animation.get("period",2.0)))
            shift=(elapsed%period)/period
            return [self._hsv((i/self.count+shift)%1.0,1,1) for i in range(self.count)],brightness
        if effect in {"breathing","pulse"}:
            period=max(0.05,float(animation.get("period",2.5)))
            phase=(elapsed%period)/period
            level=(1-math.cos(phase*2*math.pi))/2 if effect=="breathing" else max(0.0,math.sin(phase*math.pi))
            color=self._color(animation.get("color",[255,255,255]))
            return [self._scale_color(color,level)]*self.count,brightness
        if effect in {"spinner","wave","chase"}:
            period=max(0.05,float(animation.get("period",1.5)))
            head=int((elapsed%period)/period*self.count)
            tail=max(1,int(animation.get("tail",5)))
            color=self._color(animation.get("color",[255,255,255]))
            frame=[]
            for i in range(self.count):
                distance=(head-i)%self.count
                level=max(0.0,1-distance/tail) if distance<tail else 0.0
                if effect=="wave":level*=level
                frame.append(self._scale_color(color,level))
            return frame,brightness
        if effect=="ola":
            period=max(0.1,float(animation.get("period",4.0)))
            width=max(0.5,float(animation.get("width",8)))
            center=(elapsed%period)/period*self.count
            color=self._color(animation.get("color",[0,120,255]))
            return [self._scale_color(color,max(0.0,1-abs(((i-center+self.count/2)%self.count)-self.count/2)/width)**1.4) for i in range(self.count)],brightness
        if effect=="comet":
            period=max(.05,float(animation.get("period",2.0)))
            tail=max(1,int(animation.get("tail",10)))
            head=(elapsed%period)/period*self.count
            primary=self._color(animation.get("color",[255,120,0]))
            secondary=self._color(animation.get("secondary",[0,255,180]))
            frame=[]
            for i in range(self.count):
                distance=(head-i)%self.count
                strength=max(0.0,1-distance/tail)**1.5 if distance<tail else 0.0
                blend=min(1.0,distance/max(1,tail-1))
                color=tuple(round(primary[c]*(1-blend)+secondary[c]*blend) for c in range(3))
                frame.append(self._scale_color(color,strength))
            return frame,brightness
        if effect=="sparkle":
            period=max(.04,float(animation.get("period",.12)))
            tick=int(elapsed/period)
            density=max(0.0,min(1.0,float(animation.get("density",.25))))
            palette=[self._color(c) for c in animation.get("colors",[[255,255,255]])]
            rng=random.Random(tick)
            return [self._scale_color(rng.choice(palette),rng.uniform(.35,1.0)) if rng.random()<density else (0,0,0) for _ in range(self.count)],brightness
        if effect=="flash":
            period=max(0.02,float(animation.get("period",0.2)))
            color=self._color(animation.get("color",[255,255,255])) if (elapsed%period)<period/2 else (0,0,0)
            return [color]*self.count,brightness
        if effect=="fire":
            colors=[self._color(c) for c in animation.get("colors",[[255,0,0],[255,120,0],[255,255,80]])]
            period=max(0.02,float(animation.get("period",0.08)))
            random.seed(int(elapsed/period))
            return [self._scale_color(random.choice(colors),random.uniform(0.35,1.0)) for _ in range(self.count)],brightness
        raise ValueError(f"Unsupported LED effect: {effect}")

    def _render_sequence(self,animation,elapsed):
        steps=animation.get("steps",[])
        if not steps:return [(0,0,0)]*self.count,1.0
        durations=[max(0.001,float(step.get("duration",0.1))) for step in steps]
        total=sum(durations)
        position=elapsed%total if animation.get("loop",True) else min(elapsed,total-0.0001)
        cursor=0.0
        for step,duration in zip(steps,durations):
            if position<cursor+duration:
                local=position-cursor
                if "animation" in step:
                    target=self.animations.get(step["animation"])
                    if target is None:raise ValueError(f"Unknown nested LED animation: {step['animation']}")
                    return self._render(target,local)
                inline=dict(step)
                inline["type"]=inline.pop("effect","off")
                return self._render(inline,local)
            cursor+=duration
        return [(0,0,0)]*self.count,1.0

    def _show(self,frame):
        values=list(reversed(frame)) if self.reversed else frame
        payload=b"".join(struct.pack("<I",r|(g<<8)|(b<<16)) for r,g,b in values)
        fd=self._open_device()
        try:
            written=os.write(fd,payload)
            if written!=len(payload):raise RuntimeError(f"Incomplete LED write: {written}/{len(payload)} bytes")
        finally:
            os.close(fd)

    def close(self): self._show([(0,0,0)]*self.count)

    @staticmethod
    def _color(value): return tuple(max(0,min(255,int(v))) for v in value[:3])
    @staticmethod
    def _hsv(h,s,v): return tuple(round(c*255) for c in colorsys.hsv_to_rgb(h,s,v))
    @staticmethod
    def _scale_color(color,level): return tuple(round(c*max(0.0,min(1.0,level))) for c in color)
    @classmethod
    def _scale(cls,frame,level): return [cls._scale_color(color,level) for color in frame]
