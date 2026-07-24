import json
from pathlib import Path

class FakeLEDController:
    def __init__(self,config_path=None):
        path=Path(config_path) if config_path else Path(__file__).resolve().parent.parent/"config"/"leds.json"
        with path.open(encoding="utf-8") as file:self.config=json.load(file)
        self.modes=self.config["modes"]
        self.links=self.config.get("links",{})
        self.mode="off"
        self.animation_name=self.modes["off"]["animation"]
        print("[FakeLED] ready")

    def set_mode(self,name):
        if name not in self.modes:raise ValueError(f"Unknown LED mode: {name}")
        self.mode=name
        self.animation_name=self.modes[name]["animation"]
        print(f"[FakeLED] {name} -> {self.animation_name}")
        return True

    def play(self,name): return self.set_mode(name)
    def off(self): return self.set_mode("off")
    def rainbow(self): return self.set_mode("rainbow")
    def police(self): return self.set_mode("police")
    def fire(self): return self.set_mode("fire")
    def ocean(self): return self.set_mode("wave")
    def static(self,color): print(f"[FakeLED] static {color}")
    def breathing(self,color): print(f"[FakeLED] breathing {color}")
    def linked_mode(self,group,name): return self.links.get(group,{}).get(name)
    def update(self,now=None): return False
    def close(self): pass
