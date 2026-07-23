import json
import subprocess
import threading
from pathlib import Path
from robot.assets.assets import AssetError,get_asset
from robot.utils.logger import log

class Speaker:
    SUPPORTED_EXTENSIONS={".wav",".mp3"}

    def __init__(self):
        config_path=Path(__file__).resolve().parent.parent/"config"/"audio"/"speaker.json"
        with config_path.open(encoding="utf-8") as file:self.config=json.load(file)
        self.device=self.config.get("device","plughw:CARD=MAX98357A,DEV=0")
        self.volume=int(self.config.get("volume",100))
        self.process=None
        self.lock=threading.Lock()
        log.info(f"[SPEAKER] ready device={self.device}")

    def play(self,name):
        try:asset=get_asset("audio",name)
        except AssetError as error:
            log.error(f"[SPEAKER] {error}")
            return False
        path=asset.get("path")
        if path is None or not path.is_file():
            log.error(f"[SPEAKER] missing file: {name}")
            return False
        extension=path.suffix.lower()
        if extension not in self.SUPPORTED_EXTENSIONS:
            log.error(f"[SPEAKER] unsupported format: {extension}")
            return False
        command=self._command(path,extension)
        with self.lock:
            self._stop_locked()
            try:self.process=subprocess.Popen(command,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,text=True)
            except OSError as error:
                log.error(f"[SPEAKER] unable to start player: {error}")
                return False
        log.info(f"[SPEAKER] play {name} ({path.name})")
        threading.Thread(target=self._watch,args=(name,self.process),daemon=True).start()
        return True

    def _command(self,path,extension):
        if extension==".wav":return ["aplay","-q","-D",self.device,str(path)]
        return ["mpg123","-q","-a",self.device,str(path)]

    def _watch(self,name,process):
        _,stderr=process.communicate()
        if process.returncode and process.returncode not in (-15,-9):
            log.error(f"[SPEAKER] {name} failed ({process.returncode}): {(stderr or '').strip()}")
        with self.lock:
            if self.process is process:self.process=None

    def stop(self):
        with self.lock:self._stop_locked()

    def _stop_locked(self):
        if self.process is None:return
        if self.process.poll() is None:
            self.process.terminate()
            try:self.process.wait(timeout=1)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait()
        self.process=None

    def set_volume(self,volume):
        self.volume=max(0,min(100,int(volume)))
        log.info(f"[SPEAKER] volume {self.volume}")
