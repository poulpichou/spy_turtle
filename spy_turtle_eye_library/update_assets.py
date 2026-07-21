#!/usr/bin/env python3
import json
from pathlib import Path

path=Path("robot/assets/assets.json")
data=json.loads(path.read_text(encoding="utf-8"))
eyes=data["eyes"]["assets"]
eyes["angry_left"]={"label":"Angry left","type":"eye","file":"eyes/angry_left.eye"}
eyes["angry_right"]={"label":"Angry right","type":"eye","file":"eyes/angry_right.eye"}
path.write_text(json.dumps(data,indent=2)+"\n",encoding="utf-8")
print("assets.json updated")
