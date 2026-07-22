import json
from pathlib import Path

class FakeLEDController:
    def __init__(self):
        path=Path(__file__).resolve().parent.parent/"config"/"leds"/"modes.json"
        with path.open(encoding="utf-8") as file:self.config=json.load(file)
        self.mode="off"
        self.profile=self.config["modes"]["off"]
        print("[FakeLED] ready")

    def play(self,name):
        profile=self.config["modes"].get(name)
        if profile is None:
            print(f"[FakeLED] unknown mode: {name}")
            return False
        self.mode=name
        self.profile=profile
        print(f"[FakeLED] {name} {profile}")
        return True

    def set_mode(self,mode): return self.play(mode)
    def off(self): self.play("off")
    def static(self,color): print(f"[FakeLED] static {color}")
    def breathing(self,color): print(f"[FakeLED] breathing {color}")
    def rainbow(self): self.play("rainbow")
    def police(self): print("[FakeLED] police")
    def fire(self): print("[FakeLED] fire")
    def ocean(self): print("[FakeLED] ocean")
