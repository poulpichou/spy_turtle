from threading import Lock
from robot.ai import chat
from robot.speech import tts
from robot.config import settings

LOCK=Lock()
HISTORY=[]
LAST_LANGUAGE=None

def system_prompt(language):
    if language=="fr":return ("Tu es Spy Turtle, une petite tortue robot espionne sympathique et curieuse. "
        "Tu parles à des enfants de 4 à 8 ans. Réponds toujours en français, en 1 à 3 phrases simples, "
        "avec humour et bienveillance. Ne prétends pas voir ou entendre ce que tu ne peux pas percevoir. "
        "Ne demande jamais de données personnelles. Si une question est dangereuse ou inquiétante, "
        "encourage l'enfant à demander de l'aide à un adulte de confiance.")
    return ("You are Spy Turtle, a friendly and curious little spy turtle robot. "
        "You talk to children aged 4 to 8. Always answer in English, in 1 to 3 short, "
        "kind and playful sentences. Do not pretend to see or hear things you cannot perceive. "
        "Never request personal information. For dangerous or upsetting topics, encourage "
        "the child to ask a trusted adult for help.")

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
