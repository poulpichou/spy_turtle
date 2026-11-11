import json
import time
from threading import Thread
from robot.utils.logger import log
from urllib.request import Request,urlopen
from urllib.error import URLError,HTTPError
from robot.config import settings

def _request(endpoint,payload):
    request=Request(settings.CHAT_OLLAMA_URL.rstrip("/")+endpoint,data=json.dumps(payload).encode("utf-8"),headers={"Content-Type":"application/json"},method="POST")
    with urlopen(request,timeout=settings.CHAT_TIMEOUT) as response:return json.load(response)

def preload():
    if not settings.CHAT_KEEP_LOADED:return
    started=time.monotonic()
    try:
        # Use the same /api/chat endpoint, options and static system message as real requests.
        # A system-only warmup primes the prefix; cache retention is managed by Ollama.
        if settings.CHAT_STATIC_PROMPT_PRELOAD:
            from robot.brain import conversation
            from robot.speech import tts
            lang=tts.language()
            messages=[{"role":"system","content":conversation.system_prompt(lang)}]
            payload={"model":settings.CHAT_MODEL,"messages":messages,"stream":False,"keep_alive":-1,"options":{"num_predict":1,"temperature":settings.CHAT_TEMPERATURE,"num_ctx":settings.CHAT_CONTEXT_SIZE}}
            data=_request("/api/chat",payload)
            log.info(f"[LLM PRELOAD] mode=static-prefix language={lang} elapsed={time.monotonic()-started:.2f}s prompt_tokens={data.get('prompt_eval_count','?')} prompt_ms={data.get('prompt_eval_duration',0)/1e6:.0f}")
        else:
            _request("/api/generate",{"model":settings.CHAT_MODEL,"keep_alive":-1})
            log.info(f"[LLM PRELOAD] mode=model-only elapsed={time.monotonic()-started:.2f}s")
    except (URLError,TimeoutError,OSError,ValueError,RuntimeError,KeyError) as error:log.warn(f"[LLM PRELOAD] failed: {error}")

def preload_async():
    if settings.CHAT_KEEP_LOADED:Thread(target=preload,name="ollama-preload",daemon=True).start()

def reply(messages):
    payload={"model":settings.CHAT_MODEL,"messages":messages,"stream":False,"options":{"num_predict":settings.CHAT_MAX_TOKENS,"temperature":settings.CHAT_TEMPERATURE,"num_ctx":settings.CHAT_CONTEXT_SIZE}}
    if settings.CHAT_KEEP_LOADED:payload["keep_alive"]=-1
    started=time.monotonic()
    try:data=_request("/api/chat",payload)
    except (URLError,TimeoutError,OSError) as error:raise RuntimeError(f"Ollama unavailable: {error}") from error
    elapsed=time.monotonic()-started
    log.info(f"[LLM TIMING] total={elapsed:.2f}s model={settings.CHAT_MODEL} prompt_tokens={data.get('prompt_eval_count','?')} generated_tokens={data.get('eval_count','?')} load_ms={data.get('load_duration',0)/1e6:.0f} prompt_ms={data.get('prompt_eval_duration',0)/1e6:.0f} generation_ms={data.get('eval_duration',0)/1e6:.0f}")
    answer=data.get("message",{}).get("content","").strip()
    if not answer:raise RuntimeError("Ollama returned an empty response")
    return answer
