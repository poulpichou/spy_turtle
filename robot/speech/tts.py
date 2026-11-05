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
VOICES={"en":{"bryce":"en_US-bryce","amy":"en_US-amy","alba":"en_GB-alba","northern_english_male":"en_GB-northern_english_male"},"fr":{"gilles":"fr_FR-gilles","tom":"fr_FR-tom","upmc":"fr_FR-upmc"}}
DEFAULT_VOICES={"en":"bryce","fr":"gilles"}

def _preferences():
    try:
        value=json.loads(PREFERENCE_PATH.read_text(encoding="utf-8"))
        return value if isinstance(value,dict) else {}
    except (OSError,ValueError,TypeError):return {}

def _save(data):
    PREFERENCE_PATH.parent.mkdir(parents=True,exist_ok=True)
    temp=PREFERENCE_PATH.with_suffix(".tmp")
    temp.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    temp.replace(PREFERENCE_PATH)

def language():
    with LOCK:
        value=_preferences().get("language")
        return value if value in LANGUAGES else settings.TURTLE_LANGUAGE

def set_language(value):
    if value not in LANGUAGES:raise ValueError("Language must be 'fr' or 'en'")
    with LOCK:
        data=_preferences();data["language"]=value;_save(data)
    return language()

def selected_voice(lang):
    if lang not in LANGUAGES:raise ValueError("Unsupported language")
    with LOCK:value=_preferences().get("voices",{}).get(lang) if isinstance(_preferences().get("voices"),dict) else None
    return value if value in VOICES[lang] else DEFAULT_VOICES[lang]

def set_voice(lang,voice):
    if lang not in LANGUAGES or voice not in VOICES.get(lang,{}):raise ValueError("Unsupported voice or language")
    with LOCK:
        data=_preferences();voices=data.get("voices",{})
        if not isinstance(voices,dict):voices={}
        voices[lang]=voice;data["voices"]=voices;_save(data)
    return status()

def voice_path(lang):
    voice=selected_voice(lang);prefix=VOICES[lang][voice];folder=ROOT/"models"/"voices"
    # Piper voice filenames can vary in quality (low/medium/high).
    candidates=sorted(folder.glob(prefix+"-*.onnx")) if folder.is_dir() else []
    candidates += [folder/(prefix+".onnx")]
    for path in candidates:
        if path.is_file():return path
    return candidates[0] if candidates else folder/(prefix+"-medium.onnx")

def status():
    lang=language();model=voice_path(lang)
    available={key:{voice:voice_path_for(key,voice).is_file() for voice in VOICES[key]} for key in LANGUAGES}
    return {"language":lang,"languages":list(LANGUAGES),"enabled":settings.TTS_ENABLED,"voice_available":model.is_file(),"voice":model.name,"selected_voices":{key:selected_voice(key) for key in LANGUAGES},"available_voices":available,"voice_options":{key:list(VOICES[key]) for key in LANGUAGES}}

def voice_path_for(lang,voice):
    prefix=VOICES[lang][voice];folder=ROOT/"models"/"voices"
    matches=sorted(folder.glob(prefix+"-*.onnx")) if folder.is_dir() else []
    for path in [*matches,folder/(prefix+".onnx")]:
        if path.is_file():return path
    return folder/(prefix+"-medium.onnx")

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
            command=[sys.executable,"-m","piper","-m",str(model),"-f",str(path),"--",text]
            result=subprocess.run(command,capture_output=True,text=True,timeout=settings.TTS_TIMEOUT)
            if result.returncode:raise RuntimeError((result.stderr or "Piper failed").strip()[-400:])
            if not path.is_file() or path.stat().st_size<44:raise RuntimeError("Piper produced no audio")
            if not robot.speaker.play_file(path,"tts",delete_after=True):raise RuntimeError("Speaker playback failed")
            return {"ok":True,"language":lang,"voice":selected_voice(lang),"text":text}
        except Exception:
            path.unlink(missing_ok=True)
            raise
