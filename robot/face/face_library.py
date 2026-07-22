import json
from pathlib import Path
from robot.assets.assets import get_asset,get_asset_names

class FaceLibrary:
    def __init__(self):
        config_dir=Path(__file__).resolve().parent.parent/"config"/"face"
        with (config_dir/"sequences.json").open(encoding="utf-8") as file:self.sequences=json.load(file)
        self.eyes={name:self._load_eye(get_asset("eyes",name)["path"]) for name in get_asset_names("eyes")}

    def _load_eye(self,path):
        with Path(path).open(encoding="utf-8") as file:
            return [line for raw_line in file if (line:=raw_line.strip()) and not line.startswith("size:")]

    def get(self,name): return self.sequences.get(name)
    def get_eye(self,name): return self.eyes.get(name)
    def get_led(self,name):
        sequence=self.get(name)
        return sequence.get("led") if sequence else None
