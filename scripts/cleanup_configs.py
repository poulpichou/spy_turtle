#!/usr/bin/env python3
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
ASSETS=ROOT/"robot"/"assets"
CONFIG=ROOT/"robot"/"config"

def compact(value,indent=0,max_inline=180):
    pad="  "*indent
    if isinstance(value,dict):
        if not value:return "{}"
        one=json.dumps(value,ensure_ascii=False,separators=(", ",": "))
        if len(one)<=max_inline and all(not isinstance(v,dict) for v in value.values()):return one
        lines=[f'{"  "*(indent+1)}{json.dumps(k,ensure_ascii=False)}: {compact(v,indent+1,max_inline)}' for k,v in value.items()]
        return "{\n"+",\n".join(lines)+"\n"+pad+"}"
    if isinstance(value,list):
        if not value:return "[]"
        one=json.dumps(value,ensure_ascii=False,separators=(", ",": "))
        if len(one)<=max_inline:return one
        return "[\n"+",\n".join(f'{"  "*(indent+1)}{compact(v,indent+1,max_inline)}' for v in value)+"\n"+pad+"]"
    return json.dumps(value,ensure_ascii=False)

def load(path):
    with path.open(encoding="utf-8-sig") as f:return json.load(f)

def write_json(path,data): path.write_text(compact(data)+"\n",encoding="utf-8")

def normalized_stem(path): return path.stem.lower().replace("-","_").replace(" ","_")

def shell_asset_names():
    folder=ASSETS/"images"
    return {normalized_stem(p) for p in folder.iterdir() if p.suffix.lower() in {".gif",".png",".jpg",".jpeg",".webp"}}

def eye_asset_names(): return {normalized_stem(p) for p in (ASSETS/"eyes").glob("*.eye")}

def clean_leds():
    path=CONFIG/"leds.json";data=load(path);modes=data.get("modes",{})
    if modes.get("red",{}).get("label","").lower().endswith("test"):modes.pop("red",None)
    animations=data.get("animations",{});reachable=set()
    def visit(name):
        if not name or name in reachable or name not in animations:return
        reachable.add(name);animation=animations[name]
        if animation.get("type")=="sequence":
            for step in animation.get("steps",[]):
                if "animation" in step:visit(step["animation"])
    for mode in modes.values():visit(mode.get("animation"))
    data["animations"]={name:value for name,value in animations.items() if name in reachable}
    write_json(path,data)
    return set(modes)

def clean_shell_modes(shell_names,led_modes):
    path=CONFIG/"shell_modes.json";data=load(path)
    data["modes"]={name:profile for name,profile in data.get("modes",{}).items() if name in shell_names}
    for name,profile in data["modes"].items():
        led=profile.get("led")
        if led and led not in led_modes:raise SystemExit(f"shell mode {name!r} references missing LED mode {led!r}")
    fallback=data.get("fallback",{})
    if fallback.get("led") and fallback["led"] not in led_modes:raise SystemExit(f"shell fallback references missing LED mode {fallback['led']!r}")
    write_json(path,data)

def validate_faces(eyes,led_modes):
    path=CONFIG/"face"/"sequences.json";data=load(path)
    for name,sequence in data.items():
        led=sequence.get("led")
        if led and led not in led_modes:raise SystemExit(f"face sequence {name!r} references missing LED mode {led!r}")
        nxt=sequence.get("next")
        if nxt and nxt not in data:raise SystemExit(f"face sequence {name!r} references missing next sequence {nxt!r}")
        for frame in sequence.get("frames",[]):
            for side in ("left_eye","right_eye"):
                eye=frame.get(side)
                if eye not in eyes:raise SystemExit(f"face sequence {name!r} references missing eye asset {eye!r}")
    write_json(path,data)

def compact_configs():
    for path in sorted(CONFIG.rglob("*.json")):write_json(path,load(path))
    write_json(ASSETS/"assets.json",load(ASSETS/"assets.json"))

def main():
    led_modes=clean_leds();shell_names=shell_asset_names();eyes=eye_asset_names()
    clean_shell_modes(shell_names,led_modes);validate_faces(eyes,led_modes);compact_configs()
    sounds=[p for p in (ASSETS/"sounds").iterdir() if p.suffix.lower() in {".wav",".mp3"}]
    print(f"Assets: {len(shell_names)} shell images, {len(eyes)} eye files, {len(sounds)} sounds")
    print(f"LED modes: {len(led_modes)}")
    print("Configs validated and compacted.")

if __name__=="__main__":main()
