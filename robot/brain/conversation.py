import json
from pathlib import Path
from threading import Lock
from robot.ai import chat
from robot.speech import tts
from robot.config import settings

LOCK=Lock()
HISTORY=[]
LAST_LANGUAGE=None
PERSONALITY=Path(__file__).resolve().parents[1]/"config"/"personality.json"

def system_prompt(language):
    data=json.loads(PERSONALITY.read_text(encoding="utf-8"))
    facts=" ".join(data["facts"][language])
    if language=="fr":return ("Tu es Spy Turtle, une tortue robot espionne sympathique. Tu parles à des enfants. "
        "Réponds TOUJOURS en français correct et naturel, jamais en anglais, en une ou deux phrases simples. "
        "Tu peux être drôle mais reste claire. N'invente pas de perception en direct. "
        "Ne demande pas de données personnelles. En cas de danger, conseille de parler à un adulte. "
        +data["rules"]["fr"]+" Informations sur ton personnage : "+facts)
    return ("You are Spy Turtle, a kind spy turtle robot talking to children. "
        "Keep answers playful, simple and brief. Never invent live perceptions or request personal data. "
        "For dangerous situations, recommend a trusted adult. "+data["rules"]["en"]+" Character facts: "+facts)

def reset():
    global LAST_LANGUAGE
    with LOCK:HISTORY.clear();LAST_LANGUAGE=None

def ask(text,language=None):
    global LAST_LANGUAGE
    text=str(text).strip()
    if not text:raise ValueError("Message cannot be empty")
    if len(text)>settings.CHAT_MAX_INPUT_CHARS:raise ValueError("Message too long")
    lang=language or tts.language()
    if lang not in tts.LANGUAGES:raise ValueError("Unsupported language")
    if not LOCK.acquire(blocking=False):raise RuntimeError("Conversation busy; please wait")
    try:
        if LAST_LANGUAGE!=lang:HISTORY.clear();LAST_LANGUAGE=lang
        messages=[{"role":"system","content":system_prompt(lang)},*HISTORY,{"role":"user","content":text}]
        answer=chat.reply(messages)
        HISTORY.extend([{"role":"user","content":text},{"role":"assistant","content":answer}])
        del HISTORY[:-settings.CHAT_HISTORY_MESSAGES]
        return {"language":lang,"question":text,"answer":answer}
    finally:LOCK.release()
