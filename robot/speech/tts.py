import json
import subprocess
import sys
import tempfile
from pathlib import Path
from threading import RLock
from robot.config import settings
from robot.system.runtime import get_robot

ROOT=Path(__file__).resolve().parents[2]
PREFERENCE_PATH=ROOT/"robot"/"config"/"speech_preferences.json"
LOCK=RLock()
SYNTHESIS_LOCK=RLock()
LANGUAGES=("fr","en")

def language():
    with LOCK:
        try:value=json.loads(PREFERENCE_PATH.read_text(encoding="utf-8")).get("language")
        except (OSError,ValueError,TypeError):value=None
        return value if value in LANGUAGES else settings.TURTLE_LANGUAGE

def set_language(value):
    if value not in LANGUAGES:raise ValueError("Language must be 'fr' or 'en'")
    with LOCK:PREFERENCE_PATH.write_text(json.dumps({"language":value},indent=2)+"\n",encoding="utf-8")
    return language()

def voice_path(lang):
    name=settings.TTS_VOICES.get(lang)
    if not name:raise RuntimeError(f"No Piper voice configured for {lang}")
    path=Path(name)
    return path if path.is_absolute() else ROOT/path

def status():
    lang=language();model=voice_path(lang)
    return {"language":lang,"languages":list(LANGUAGES),"enabled":settings.TTS_ENABLED,"voice_available":model.is_file(),"voice":model.name}

def say(text,language=None):
    text=str(text).strip();lang=language or globals()["language"]()
    if lang not in LANGUAGES:raise ValueError("Unsupported language")
    if not text:raise ValueError("Text cannot be empty")
    if len(text)>settings.TTS_MAX_CHARS:raise ValueError("Text too long")
    if not settings.TTS_ENABLED:raise RuntimeError("TTS disabled")
    robot=get_robot()
    if robot is None or robot.speaker is None:raise RuntimeError("Speaker unavailable")
    model=voice_path(lang)
    if not model.is_file():raise RuntimeError(f"Piper voice missing: {model}")
    with SYNTHESIS_LOCK:
        with tempfile.NamedTemporaryFile(prefix="spyturtle_tts_",suffix=".wav",delete=False) as file:path=Path(file.name)
        try:
            # Uses the python -m piper CLI verified on the Pi (Piper 1.8.x).
            command=[sys.executable,"-m","piper","-m",str(model),"-f",str(path),"--",text]
            result=subprocess.run(command,capture_output=True,text=True,timeout=settings.TTS_TIMEOUT)
            if result.returncode:raise RuntimeError((result.stderr or "Piper failed").strip()[-400:])
            if not path.is_file() or path.stat().st_size<44:raise RuntimeError("Piper produced no audio")
            if not robot.speaker.play_file(path,"tts",delete_after=True):raise RuntimeError("Speaker playback failed")
            return {"ok":True,"language":lang,"text":text}
        except Exception:
            path.unlink(missing_ok=True)
            raise
