import json
import random
import time
from pathlib import Path
from threading import Thread
from robot.speech import tts
from robot.utils.logger import log

CONFIG=Path(__file__).resolve().parents[1]/"config"/"sentinel.json"

class Sentinel:
    def __init__(self):
        self.config=json.loads(CONFIG.read_text(encoding="utf-8"));self.seen=set();self.last_greet={};
    def status(self):return {"enabled":bool(self.config["enabled"]),"cooldown_seconds":self.config["cooldown_seconds"]}
    def set_enabled(self,enabled):
        self.config["enabled"]=bool(enabled)
        CONFIG.write_text(json.dumps(self.config,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        self.seen.clear();return self.status()
    def update(self,robot):
        now=time.monotonic()
        if not self.config["enabled"]:return
        # Only greet newly added names in detected_recent, not every timestamp refresh.
        current={str(item.get("name","")).strip() for item in robot.state.vision.get("detected_recent",[])}
        current={name for name in current if name and name.lower()!="unknown"}
        new=current-self.seen;self.seen=current
        for name in sorted(new):
            if now-self.last_greet.get(name,-1e9)<self.config["cooldown_seconds"]:continue
            self.last_greet[name]=now;self.greet(robot,name);break
    def greet(self,robot,name):
        lang=tts.language();phrases=self.config["phrases"].get(lang,self.config["phrases"]["en"])
        phrase=random.choice(phrases).format(name=name.replace("_"," "))
        log.info(f"[SENTINEL] greeting {name}: {phrase}")
        if robot.face:
            try:robot.face.play("blink")
            except Exception as error:log.warn(f"[SENTINEL] blink: {error}")
        Thread(target=self._speak,args=(phrase,lang),daemon=True).start()
    @staticmethod
    def _speak(phrase,lang):
        try:tts.say(phrase,language=lang)
        except Exception as error:log.warn(f"[SENTINEL] speech: {error}")
