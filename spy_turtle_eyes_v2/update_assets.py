#!/usr/bin/env python3
import json
from pathlib import Path

path=Path("robot/assets/assets.json")
data=json.loads(path.read_text(encoding="utf-8"))
data["eyes"]["default"]="open"
data["eyes"]["assets"]={
    "open": {
        "label": "Neutral",
        "type": "eye",
        "file": "eyes/open.eye"
    },
    "half": {
        "label": "Half open",
        "type": "eye",
        "file": "eyes/half.eye"
    },
    "sleepy": {
        "label": "Sleepy",
        "type": "eye",
        "file": "eyes/sleepy.eye"
    },
    "closed": {
        "label": "Closed",
        "type": "eye",
        "file": "eyes/closed.eye"
    },
    "happy": {
        "label": "Happy heart",
        "type": "eye",
        "file": "eyes/happy.eye"
    },
    "surprised": {
        "label": "Surprised",
        "type": "eye",
        "file": "eyes/surprised.eye"
    },
    "sleeping": {
        "label": "Sleeping",
        "type": "eye",
        "file": "eyes/sleeping.eye"
    },
    "angry_left": {
        "label": "Angry left",
        "type": "eye",
        "file": "eyes/angry_left.eye"
    },
    "angry_right": {
        "label": "Angry right",
        "type": "eye",
        "file": "eyes/angry_right.eye"
    },
    "look_left_1": {
        "label": "Look left 1",
        "type": "eye",
        "file": "eyes/look_left_1.eye"
    },
    "look_left_2": {
        "label": "Look left 2",
        "type": "eye",
        "file": "eyes/look_left_2.eye"
    },
    "look_left": {
        "label": "Look left",
        "type": "eye",
        "file": "eyes/look_left.eye"
    },
    "look_right_1": {
        "label": "Look right 1",
        "type": "eye",
        "file": "eyes/look_right_1.eye"
    },
    "look_right_2": {
        "label": "Look right 2",
        "type": "eye",
        "file": "eyes/look_right_2.eye"
    },
    "look_right": {
        "label": "Look right",
        "type": "eye",
        "file": "eyes/look_right.eye"
    },
    "look_up_1": {
        "label": "Look up 1",
        "type": "eye",
        "file": "eyes/look_up_1.eye"
    },
    "look_up_2": {
        "label": "Look up 2",
        "type": "eye",
        "file": "eyes/look_up_2.eye"
    },
    "look_up": {
        "label": "Look up",
        "type": "eye",
        "file": "eyes/look_up.eye"
    },
    "look_down_1": {
        "label": "Look down 1",
        "type": "eye",
        "file": "eyes/look_down_1.eye"
    },
    "look_down_2": {
        "label": "Look down 2",
        "type": "eye",
        "file": "eyes/look_down_2.eye"
    },
    "look_down": {
        "label": "Look down",
        "type": "eye",
        "file": "eyes/look_down.eye"
    }
}
path.write_text(json.dumps(data,indent=2)+"\n",encoding="utf-8")
print("assets.json updated")
