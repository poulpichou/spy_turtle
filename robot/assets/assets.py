import json
import re
from copy import deepcopy
from pathlib import Path

ASSETS_DIR=Path(__file__).resolve().parent
CONFIG_FILE=ASSETS_DIR/"assets.json"
CONFIG_DIR=ASSETS_DIR.parent/"config"

class AssetError(Exception): pass

def _slug(value): return re.sub(r"[^a-zA-Z0-9]+","_",value).strip("_").lower()
def _label(value):
    value=re.sub(r"([a-zA-Z])([0-9]+)$",r"\1 \2",value)
    return value.replace("_"," ").replace("-"," ").strip().title()

class AssetCatalog:
    def __init__(self,config_file=CONFIG_FILE,assets_dir=ASSETS_DIR):
        self.config_file=Path(config_file);self.assets_dir=Path(assets_dir);self.data=self._load()

    def _load(self):
        if not self.config_file.is_file():raise AssetError(f"Asset configuration not found: {self.config_file}")
        try:
            with self.config_file.open(encoding="utf-8") as file:data=json.load(file)
        except json.JSONDecodeError as error:raise AssetError(f"Invalid asset configuration: {error}") from error
        if not isinstance(data,dict):raise AssetError("Asset configuration root must be an object")
        self._discover_shell(data);self._discover_eyes(data);self._discover_audio(data);self._discover_fonts(data);self._discover_faces(data);self._discover_led_modes(data)
        return data

    def _section(self,data,name):
        section=data.setdefault(name,{})
        section.setdefault("assets",{})
        return section

    def _merge_discovered(self,data,section_name,discovered):
        section=self._section(data,section_name);overrides=section.get("assets",{});merged={}
        for name,asset in discovered.items():
            override=overrides.get(name,{}) if isinstance(overrides,dict) else {}
            merged[name]={**asset,**override}
        section["assets"]=merged

    def _discover_shell(self,data):
        folder=self.assets_dir/"images";discovered={}
        if folder.is_dir():
            for path in sorted(folder.iterdir()):
                ext=path.suffix.lower()
                if ext not in {".gif",".png",".jpg",".jpeg",".webp"}:continue
                name=_slug(path.stem);discovered[name]={"label":_label(path.stem),"type":"gif" if ext==".gif" else "image","file":f"images/{path.name}","rotation":0,"resize":True}
        self._merge_discovered(data,"shell",discovered)

    def _discover_eyes(self,data):
        folder=self.assets_dir/"eyes";discovered={}
        if folder.is_dir():
            for path in sorted(folder.glob("*.eye")):
                name=_slug(path.stem);discovered[name]={"label":_label(path.stem),"type":"eye","file":f"eyes/{path.name}"}
        self._merge_discovered(data,"eyes",discovered)

    def _discover_audio(self,data):
        folder=self.assets_dir/"sounds";discovered={}
        if folder.is_dir():
            for path in sorted(folder.iterdir()):
                if path.suffix.lower() not in {".wav",".mp3"}:continue
                name=_slug(path.stem);category=name.split("_",1)[0]
                discovered[name]={"label":_label(path.stem),"type":"sound","file":f"sounds/{path.name}","tags":[category]}
        self._merge_discovered(data,"audio",discovered)

    def _discover_fonts(self,data):
        folder=self.assets_dir/"fonts";discovered={}
        if folder.is_dir():
            for path in sorted(folder.iterdir()):
                if path.suffix.lower() not in {".ttf",".otf"}:continue
                name=_slug(path.stem);discovered[name]={"label":_label(path.stem),"type":"font","file":f"fonts/{path.name}"}
        self._merge_discovered(data,"fonts",discovered)

    def _discover_faces(self,data):
        path=CONFIG_DIR/"face"/"sequences.json";discovered={}
        if path.is_file():
            with path.open(encoding="utf-8") as file:sequences=json.load(file)
            for name in sequences:discovered[name]={"label":_label(name),"type":"face_sequence"}
        self._merge_discovered(data,"faces",discovered)

    def _discover_led_modes(self,data):
        path=CONFIG_DIR/"leds.json";discovered={}
        if path.is_file():
            with path.open(encoding="utf-8") as file:config=json.load(file)
            for name,mode in config.get("modes",{}).items():discovered[name]={"label":mode.get("label",_label(name)),"type":"led_mode"}
        self._merge_discovered(data,"leds",discovered)

    def reload(self): self.data=self._load();return self
    def sections(self): return tuple(self.data)
    def section(self,name):
        section=self.data.get(name)
        if not isinstance(section,dict):raise AssetError(f"Unknown asset section: {name}")
        return section
    def default(self,section): return self.section(section).get("default")
    def assets(self,section):
        assets=self.section(section).get("assets",{})
        if not isinstance(assets,dict):raise AssetError(f"Invalid assets section: {section}")
        return deepcopy(assets)
    def names(self,section): return tuple(self.assets(section))
    def get(self,section,name=None):
        if name is None:name=self.default(section)
        if name is None:raise AssetError(f"No default asset configured for section: {section}")
        asset=self.assets(section).get(name)
        if asset is None:raise AssetError(f"Unknown asset: {section}.{name}")
        asset["name"]=name;asset["section"]=section
        if "file" in asset:asset["path"]=self.resolve(asset["file"])
        return asset
    def resolve(self,file):
        path=(self.assets_dir/file).resolve()
        try:path.relative_to(self.assets_dir.resolve())
        except ValueError as error:raise AssetError(f"Asset path escapes assets directory: {file}") from error
        return path
    def exists(self,section,name=None):
        try:asset=self.get(section,name)
        except AssetError:return False
        path=asset.get("path");return path is None or path.is_file()
    def available(self,section): return {name:asset for name in self.names(section) if (asset:=self.get(section,name)).get("available",True) and self.exists(section,name)}

assets=AssetCatalog()
def get_asset(section,name=None): return assets.get(section,name)
def get_assets(section): return assets.available(section)
def get_asset_names(section): return tuple(assets.available(section))
def get_default_asset(section): return assets.default(section)
def exists(section,name=None): return assets.exists(section,name)
def available(section): return assets.available(section)
def reload(): return assets.reload()
def resolve(file): return assets.resolve(file)
