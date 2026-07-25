import json
from copy import deepcopy
from pathlib import Path

ASSETS_DIR=Path(__file__).resolve().parent
CONFIG_FILE=ASSETS_DIR/"assets.json"

class AssetError(Exception): pass

class AssetCatalog:
    def __init__(self,config_file=CONFIG_FILE,assets_dir=ASSETS_DIR):
        self.config_file=Path(config_file)
        self.assets_dir=Path(assets_dir)
        self.data=self._load()

    def _load(self):
        if not self.config_file.is_file():raise AssetError(f"Asset configuration not found: {self.config_file}")
        try:
            with self.config_file.open(encoding="utf-8") as file:data=json.load(file)
        except json.JSONDecodeError as error:raise AssetError(f"Invalid asset configuration: {error}") from error
        if not isinstance(data,dict):raise AssetError("Asset configuration root must be an object")
        self._discover_shell_gifs(data)
        return data

    def _discover_shell_gifs(self,data):
        images=self.assets_dir/"images"
        if not images.is_dir():return
        shell=data.setdefault("shell",{})
        assets=shell.setdefault("assets",{})
        for path in sorted(images.glob("*.gif")):
            name=path.stem.lower().replace(" ","_").replace("-","_")
            assets.setdefault(name,{"label":path.stem.replace("_"," ").replace("-"," ").title(),"type":"gif","file":f"images/{path.name}","rotation":0,"resize":True})

    def reload(self):
        self.data=self._load()
        return self

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
        asset["name"]=name
        asset["section"]=section
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
        path=asset.get("path")
        return path is None or path.is_file()

    def available(self,section):
        return {name:asset for name in self.names(section) if (asset:=self.get(section,name)).get("available",True) and self.exists(section,name)}

assets=AssetCatalog()

def get_asset(section,name=None): return assets.get(section,name)
def get_assets(section): return assets.available(section)
def get_asset_names(section): return tuple(assets.available(section))
def get_default_asset(section): return assets.default(section)
def exists(section,name=None): return assets.exists(section,name)
def available(section): return assets.available(section)
def reload(): return assets.reload()
def resolve(file): return assets.resolve(file)
