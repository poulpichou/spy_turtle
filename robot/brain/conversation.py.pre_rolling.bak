import json
from pathlib import Path
from threading import Lock
from robot.ai import chat
from robot.speech import tts
from robot.config import settings
from robot.system.runtime import get_robot

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

def mood_prompt(language):
    robot=get_robot();state=robot.state if robot else None
    mood=str(state.mood if state else "neutral")
    if not settings.CHAT_MOOD_CONTEXT_ENABLED:return ("Humeur: " if language=="fr" else "Mood: ")+mood
    context=str((state.mood_context_fr if language=="fr" else state.mood_context_en) if state else "")
    if language=="fr":return f"Humeur: {mood}. Contexte imaginaire: {context}. Utilise-le seulement si on te demande comment tu vas, sans le présenter comme réel."
    return f"Mood: {mood}. Imaginary context: {context}. Use only if asked how you feel; do not claim it is real."

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
        limit=max(0,int(settings.CHAT_HISTORY_MESSAGES))
        history=HISTORY[-limit:] if limit else []
        # Keep the system prefix byte-for-byte identical to the startup warmup.
        messages=[{"role":"system","content":system_prompt(lang)},*history,{"role":"user","content":mood_prompt(lang)+"\n"+text}]
        answer=chat.reply(messages)
        HISTORY.extend([{"role":"user","content":text},{"role":"assistant","content":answer}])
        if limit:del HISTORY[:-limit]
        else:HISTORY.clear()
        return {"language":lang,"question":text,"answer":answer}
    finally:LOCK.release()
