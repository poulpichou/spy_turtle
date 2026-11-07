import json
import math
import time
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
        self.last_audio_stats={}
        self.output_headroom=float(self.config.get("output_headroom",0.92))
        self.adaptive_enabled=False
        self.adaptive_boost=0
        self.adaptive_max_boost=15
        self.adaptive_last_level=None
        self.adaptive_last_error=None
        self.lock=threading.Lock()
        log.info(f"[SPEAKER] ready device={self.device} volume={self.volume}%")

    def _gain(self):
        # Adaptive boost is bounded by the admin volume ceiling (100%).
        effective=min(100,self.volume+(self.adaptive_boost if self.adaptive_enabled else 0))
        return effective/self.reference_volume

    def adaptive_status(self):
        return {"enabled":self.adaptive_enabled,"boost":self.adaptive_boost,"max_boost":self.adaptive_max_boost,"ambient_rms":self.adaptive_last_level,"error":self.adaptive_last_error}

    def set_adaptive(self,enabled):
        self.adaptive_enabled=bool(enabled)
        if not enabled:self.adaptive_boost=0
        log.info(f"[AUDIO ADAPTIVE] enabled={self.adaptive_enabled}")
        return self.adaptive_status()

    def sample_ambient(self):
        # One short PCM measurement; never stores or uploads microphone recordings.
        if not self.adaptive_enabled:return self.adaptive_status()
        with self.lock:
            if self.process and self.process.poll() is None:return self.adaptive_status()
        try:
            result=subprocess.run(["arecord","-q","-D","default","-f","S16_LE","-r","16000","-c","1","-t","raw","-d","1"],capture_output=True,timeout=4)
            if result.returncode:raise RuntimeError(result.stderr.decode(errors="replace")[-180:])
            values=array("h");values.frombytes(result.stdout[:len(result.stdout)//2*2])
            if sys.byteorder!="little":values.byteswap()
            if not values:raise RuntimeError("No microphone samples")
            rms=math.sqrt(sum(v*v for v in values)/len(values))/32768
            self.adaptive_last_level=round(rms,5)
            # Conservative, intentionally coarse boost; no gain above 100%.
            desired=0 if rms<0.02 else 5 if rms<0.05 else 10 if rms<0.10 else self.adaptive_max_boost
            self.adaptive_boost=round(self.adaptive_boost*0.6+desired*0.4)
            self.adaptive_last_error=None
            log.info(f"[AUDIO AMBIENT] rms={rms:.4f} boost={self.adaptive_boost}%")
        except Exception as error:
            self.adaptive_last_error=str(error)
            self.adaptive_boost=0
            log.warn(f"[AUDIO AMBIENT] measurement unavailable: {error}")
        return self.adaptive_status()


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
        if extension==".wav":
            try:
                play_path=self._scaled_wav(path,self._gain())
                if delete_after:
                    try:path.unlink(missing_ok=True)
                    except Exception:pass
                cleanup_path=play_path
            except Exception as error:
                log.warn(f"[SPEAKER] WAV volume scaling failed, playing original: {error}")
        if extension==".wav":
            try:
                self.last_audio_stats={"source":self.analyze_wav(path if path.exists() else play_path),"output":self.analyze_wav(play_path),"gain_requested":round(self._gain(),3)}
            except Exception as error:log.warn(f"[AUDIO DIAG] {error}")
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

    def analyze_wav(self,path):
        with wave.open(str(path),"rb") as source:
            if source.getsampwidth()!=2:return {"format":"not 16-bit PCM"}
            frames=source.readframes(source.getnframes())
            rate=source.getframerate()
        values=array("h");values.frombytes(frames[:len(frames)//2*2])
        if sys.byteorder!="little":values.byteswap()
        if not values:return {"empty":True}
        peak=max(abs(v) for v in values)/32768
        clipped=sum(abs(v)>=32760 for v in values)/len(values)*100
        rms=math.sqrt(sum(v*v for v in values)/len(values))/32768
        result={"peak":round(peak,4),"rms":round(rms,4),"clipped_percent":round(clipped,3),"sample_rate":rate}
        log.info(f"[AUDIO DIAG] peak={peak:.3f} rms={rms:.3f} clipped={clipped:.2f}% rate={rate}")
        return result

    def _command(self,path,extension):
        if extension==".wav":return ["aplay","-q","-D",self.device,str(path)]
        # MP3 playback cannot use the WAV peak limiter; cap decoder gain at unity.
        scale=max(0,min(32768,round(32768*self._gain()*self.output_headroom)))
        return ["mpg123","-q","-o","alsa","-a",self.mp3_device,"-f",str(scale),str(path)]

    def _scaled_wav(self,path,gain):
        with wave.open(str(path),"rb") as source:
            params=source.getparams()
            if params.sampwidth!=2:raise ValueError(f"unsupported WAV sample width: {params.sampwidth}")
            samples=array("h",source.readframes(params.nframes))
        if sys.byteorder!="little":samples.byteswap()
        # Peak normalization prevents hard clipping when software volume exceeds reference.
        # Headroom also avoids sending full-scale samples to the I2S amplifier.
        peak=max((abs(v) for v in samples),default=0)
        ceiling=max(0.1,min(0.98,self.output_headroom))*32767
        applied=min(max(0.0,gain),ceiling/peak) if peak else max(0.0,gain)
        for index,value in enumerate(samples):samples[index]=max(-32768,min(32767,round(value*applied)))
        log.info(f"[AUDIO LIMITER] requested={gain:.3f} applied={applied:.3f} peak={peak}/32768 headroom={self.output_headroom:.2f}")
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

    def status(self): return {"volume":self.volume,"reference_volume":self.reference_volume,"device":self.device,"audio_stats":self.last_audio_stats,"adaptive":self.adaptive_status(),"output_headroom":self.output_headroom}
