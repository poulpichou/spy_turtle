import json
from pathlib import Path
from threading import Lock
from robot.ai import chat
from robot.speech import tts
from robot.config import settings
from robot.system.runtime import get_robot
from robot.utils.logger import log

LOCK=Lock()
HISTORY=[]
LAST_LANGUAGE=None
PERSONALITY=Path(__file__).resolve().parents[1]/"config"/"personality.json"

MOOD_AND_HISTORY_RULES_FR='Règles de conversation : les faits de ton personnage sont prioritaires sur les improvisations et les réponses passées. Réponds directement à la question. Utilise l’historique uniquement pour suivre le contexte, sans recopier les tournures de tes anciennes réponses. Évite de répéter les mêmes débuts de phrase, plaisanteries ou descriptions. Ton humeur module subtilement ton ton, mais ne change pas tes goûts ni tes connaissances. Ne parle pas spontanément de ton humeur et ne commence pas chaque réponse par elle ; évoque-la surtout si on te le demande. Même endormie ou somnolente, réponds normalement aux questions. '
MOOD_AND_HISTORY_RULES_EN='Conversation rules: character facts take priority over improvisation and previous answers. Answer the current question directly. Use history only to understand context, not to copy your earlier wording. Avoid repeating openings, jokes or descriptions. Mood subtly affects tone, not your preferences or knowledge. Do not mention mood in every answer or start answers with it; discuss it mainly when asked. Even when sleepy, answer questions normally. '

def system_prompt(language):
    data=json.loads(PERSONALITY.read_text(encoding="utf-8"))
    facts=" ".join(data["facts"][language])
    if language=="fr":return ("Tu es Spy Turtle, une tortue robot espionne sympathique. Tu parles à des enfants. "
        "Réponds TOUJOURS en français correct et naturel, jamais en anglais, en une ou deux phrases simples. "
        "Tu peux être drôle mais reste claire. N'invente pas de perception en direct. "
        "Ne demande pas de données personnelles. En cas de danger, conseille de parler à un adulte. "
        +data["rules"]["fr"]+" "+MOOD_AND_HISTORY_RULES_FR+" Informations sur ton personnage : "+facts)
    return ("You are Spy Turtle, a kind spy turtle robot talking to children. "
        "Keep answers playful, simple and brief. Never invent live perceptions or request personal data. "
        "For dangerous situations, recommend a trusted adult. "+data["rules"]["en"]+" "+MOOD_AND_HISTORY_RULES_EN+" Character facts: "+facts)

def mood_prompt(language):
    robot=get_robot();state=robot.state if robot else None
    mood=str(state.mood if state else "neutral")
    if not settings.CHAT_MOOD_CONTEXT_ENABLED:return ("Humeur: " if language=="fr" else "Mood: ")+mood
    context=str((state.mood_context_fr if language=="fr" else state.mood_context_en) if state else "")
    if language=="fr":return f"Humeur: {mood}. Contexte imaginaire: {context}. Utilise-le seulement si on te demande comment tu vas, sans le présenter comme réel."
    return f"Mood: {mood}. Imaginary context: {context}. Use only if asked how you feel; do not claim it is real."

def _context_log(static,history,mood,question,language):
    # Character counts are exact; token counts by component require the model's tokenizer.
    log.info(f"[LLM CONTEXT] language={language} static_chars={len(static)} history_messages={len(history)} history_chars={sum(len(m['content']) for m in history)} mood_chars={len(mood)} question_chars={len(question)} total_messages={len(history)+2} approx_chars={len(static)+sum(len(m['content']) for m in history)+len(mood)+len(question)}")
    if settings.CHAT_DEBUG_PROMPT:
        log.info("[LLM PROMPT] BEGIN\n[STATIC]\n"+static+"\n[/STATIC]\n[HISTORY]\n"+"\n".join(f"[{m['role'].upper()}] {m['content']}" for m in history)+"\n[/HISTORY]\n[MOOD] "+mood+"\n[QUESTION] "+question+"\n[LLM PROMPT] END")

def reset():
    global LAST_LANGUAGE
    with LOCK:HISTORY.clear();LAST_LANGUAGE=None
    chat.invalidate_rolling("reset")

def ask(text,language=None):
    global LAST_LANGUAGE
    text=str(text).strip()
    if not text:raise ValueError("Message cannot be empty")
    if len(text)>settings.CHAT_MAX_INPUT_CHARS:raise ValueError("Message too long")
    lang=language or tts.language()
    if lang not in tts.LANGUAGES:raise ValueError("Unsupported language")
    if not LOCK.acquire(blocking=False):raise RuntimeError("Conversation busy; please wait")
    try:
        if LAST_LANGUAGE!=lang:
            HISTORY.clear();LAST_LANGUAGE=lang;chat.invalidate_rolling("language-change")
        limit=max(0,int(settings.CHAT_HISTORY_MESSAGES))
        history=HISTORY[-limit:] if limit else []
        static=system_prompt(lang);mood=mood_prompt(lang)
        messages=[{"role":"system","content":static},*history,{"role":"user","content":mood+"\n"+text}]
        _context_log(static,history,mood,text,lang)
        answer=chat.reply(messages)
        HISTORY.extend([{"role":"user","content":text},{"role":"assistant","content":answer}])
        if limit:del HISTORY[:-limit]
        else:HISTORY.clear()
        # Prepare after the real answer, before the API starts TTS playback.
        rolling=[{"role":"system","content":static},*HISTORY]
        chat.prepare_rolling_async(rolling,lang,len(HISTORY))
        return {"language":lang,"question":text,"answer":answer}
    finally:LOCK.release()
