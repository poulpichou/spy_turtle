#!/usr/bin/env python3
import json
from pathlib import Path

# This script is executed from the root of the spy_turtle repository.
ROOT=Path.cwd().resolve()
LEDS=ROOT/"robot"/"config"/"leds.json"

if not LEDS.is_file():
    raise SystemExit(f"Expected file not found: {LEDS}\nRun this patch from the root of the spy_turtle repository.")

def load(path):
    with path.open(encoding="utf-8-sig") as f:return json.load(f)

def compact(value,indent=0,max_inline=180):
    pad="  "*indent
    if isinstance(value,dict):
        if not value:return "{}"
        one=json.dumps(value,ensure_ascii=False,separators=(", ",": "))
        if len(one)<=max_inline and all(not isinstance(v,dict) for v in value.values()):return one
        return "{\n"+",\n".join(
            f'{"  "*(indent+1)}{json.dumps(k,ensure_ascii=False)}: {compact(v,indent+1,max_inline)}'
            for k,v in value.items()
        )+"\n"+pad+"}"
    if isinstance(value,list):
        if not value:return "[]"
        one=json.dumps(value,ensure_ascii=False,separators=(", ",": "))
        if len(one)<=max_inline:return one
        return "[\n"+",\n".join(
            f'{"  "*(indent+1)}{compact(v,indent+1,max_inline)}' for v in value
        )+"\n"+pad+"]"
    return json.dumps(value,ensure_ascii=False)

data=load(LEDS)
modes=data.setdefault("modes",{})
animations=data.setdefault("animations",{})

# These modes are referenced by face sequences and existed in the old legacy
# robot/config/leds/modes.json, but were missing from the active leds.json.
modes.setdefault("dizzy",{"label":"Dizzy","animation":"dizzy"})
modes.setdefault("thinking",{"label":"Thinking","animation":"thinking"})

animations.setdefault("dizzy",{
    "type":"spinner","color":[170,50,255],"tail":6,"period":0.8,"brightness":0.8
})
animations.setdefault("thinking",{
    "type":"spinner","color":[255,170,0],"tail":4,"period":2.4,"brightness":0.55
})

LEDS.write_text(compact(data)+"\n",encoding="utf-8")
print(f"Updated: {LEDS}")
print("Added/verified LED modes: dizzy, thinking")
