import json
import subprocess
import sys
import tempfile
import threading
import wave
from array import array
from pathlib import Path
from robot.assets.assets import AssetError,get_asset
from robot.utils.logger import log

class Speaker:
    SUPPORTED_EXTENSIONS={".wav",".mp3"}

    def __init__(self):
        config_path=Path(__file__).resolve().parent.parent/"config"/"audio"/"speaker.json"
        with config_path.open(encoding="utf-8") as file:self.config=json.load(file)
        self.device=self.config.get("device","plughw:CARD=MAX98357A,DEV=0")
        self.mp3_device=self.config.get("mp3_device","hw:MAX98357A,0")
        self.volume=int(self.config.get("volume",60))
        self.reference_volume=max(1,int(self.config.get("reference_volume",60)))
        self.process=None
        self.lock=threading.Lock()
        log.info(f"[SPEAKER] ready device={self.device} volume={self.volume}%")

    def _gain(self): return self.volume/self.reference_volume

    def play(self,name):
        try:asset=get_asset("audio",name)
        except AssetError as error:
            log.error(f"[SPEAKER] {error}")
            return False
        path=asset.get("path")
        if path is None or not path.is_file():
            log.error(f"[SPEAKER] missing file: {name}")
            return False
        return self.play_file(path,name)

    def play_file(self,path,name=None,delete_after=False):
        path=Path(path)
        extension=path.suffix.lower()
        if extension not in self.SUPPORTED_EXTENSIONS:
            log.error(f"[SPEAKER] unsupported format: {extension}")
            return False
        play_path=path
        cleanup_path=path if delete_after else None
        if extension==".wav" and self._gain()!=1.0:
            try:
                play_path=self._scaled_wav(path,self._gain())
                if delete_after:
                    try:path.unlink(missing_ok=True)
                    except Exception:pass
                cleanup_path=play_path
            except Exception as error:
                log.warn(f"[SPEAKER] WAV volume scaling failed, playing original: {error}")
        command=self._command(play_path,extension)
        with self.lock:
            self._stop_locked()
            try:self.process=subprocess.Popen(command,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,text=True)
            except OSError as error:
                log.error(f"[SPEAKER] unable to start player: {error}")
                return False
        label=name or path.name
        log.info(f"[SPEAKER] play {label} ({path.name}) volume={self.volume}%")
        threading.Thread(target=self._watch,args=(label,self.process,cleanup_path),daemon=True).start()
        return True

    def _command(self,path,extension):
        if extension==".wav":return ["aplay","-q","-D",self.device,str(path)]
        scale=max(0,min(65535,round(32768*self._gain())))
        return ["mpg123","-q","-o","alsa","-a",self.mp3_device,"-f",str(scale),str(path)]

    def _scaled_wav(self,path,gain):
        with wave.open(str(path),"rb") as source:
            params=source.getparams()
            if params.sampwidth!=2:raise ValueError(f"unsupported WAV sample width: {params.sampwidth}")
            samples=array("h",source.readframes(params.nframes))
        if sys.byteorder!="little":samples.byteswap()
        for index,value in enumerate(samples):samples[index]=max(-32768,min(32767,round(value*gain)))
        if sys.byteorder!="little":samples.byteswap()
        temp=tempfile.NamedTemporaryFile(prefix="spyturtle_",suffix=".wav",delete=False)
        temp.close()
        with wave.open(temp.name,"wb") as target:
            target.setparams(params)
            target.writeframes(samples.tobytes())
        return Path(temp.name)

    def _watch(self,name,process,cleanup_path=None):
        _,stderr=process.communicate()
        if process.returncode and process.returncode not in (-15,-9):
            log.error(f"[SPEAKER] {name} failed ({process.returncode}): {(stderr or '').strip()}")
        if cleanup_path:
            try:Path(cleanup_path).unlink(missing_ok=True)
            except Exception:pass
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
        log.info(f"[SPEAKER] volume {self.volume}%")

    def status(self): return {"volume":self.volume,"reference_volume":self.reference_volume,"device":self.device}
