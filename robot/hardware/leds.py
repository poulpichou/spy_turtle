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
        self.reversed=bool(settings.get("reversed",False))
        self.modes=self.config["modes"]
        self.animations=self.config["animations"]
        self.links=self.config.get("links",{})
        self.mode="off"
        self.animation_name=self.modes["off"]["animation"]
        self.started_at=time.monotonic()
        self.last_frame_at=0.0
        self.frame_interval=1/50
        self.fd=None
        self._configure_device()
        self._show([(0,0,0)]*self.count)
        log.info(f"[LED] ready device={self.device} count={self.count}")

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
        self._show(self._scale(frame,self.global_brightness*brightness))
        return True

    def _render(self,animation,elapsed):
        effect=animation.get("type",animation.get("effect","off"))
        brightness=float(animation.get("brightness",1.0))
        if effect=="sequence":return self._render_sequence(animation,elapsed)
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
