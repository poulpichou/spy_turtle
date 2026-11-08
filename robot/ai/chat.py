import json
import time
from threading import Thread
from robot.utils.logger import log
from urllib.request import Request,urlopen
from urllib.error import URLError,HTTPError
from robot.config import settings

def preload():
    if not settings.CHAT_KEEP_LOADED:return
    payload={"model":settings.CHAT_MODEL,"keep_alive":-1}
    request=Request(settings.CHAT_OLLAMA_URL.rstrip("/")+"/api/generate",data=json.dumps(payload).encode("utf-8"),headers={"Content-Type":"application/json"},method="POST")
    started=time.monotonic()
    try:
        with urlopen(request,timeout=settings.CHAT_TIMEOUT) as response:data=json.load(response)
        log.info(f"[LLM PRELOAD] model={settings.CHAT_MODEL} elapsed={time.monotonic()-started:.2f}s")
    except (URLError,TimeoutError,OSError,ValueError) as error:log.warn(f"[LLM PRELOAD] failed: {error}")

def preload_async():
    if settings.CHAT_KEEP_LOADED:Thread(target=preload,name="ollama-preload",daemon=True).start()

def reply(messages):
    payload={"model":settings.CHAT_MODEL,"messages":messages,"stream":False,"options":{"num_predict":settings.CHAT_MAX_TOKENS,"temperature":settings.CHAT_TEMPERATURE,"num_ctx":settings.CHAT_CONTEXT_SIZE}}
    if settings.CHAT_KEEP_LOADED:payload["keep_alive"]=-1
    request=Request(settings.CHAT_OLLAMA_URL.rstrip("/")+"/api/chat",data=json.dumps(payload).encode("utf-8"),headers={"Content-Type":"application/json"},method="POST")
    started=time.monotonic()
    try:
        with urlopen(request,timeout=settings.CHAT_TIMEOUT) as response:data=json.load(response)
    except (URLError,TimeoutError,OSError) as error:raise RuntimeError(f"Ollama unavailable: {error}") from error
    elapsed=time.monotonic()-started
    log.info(f"[LLM TIMING] total={elapsed:.2f}s model={settings.CHAT_MODEL} prompt_tokens={data.get('prompt_eval_count','?')} generated_tokens={data.get('eval_count','?')} load_ms={data.get('load_duration',0)/1e6:.0f} prompt_ms={data.get('prompt_eval_duration',0)/1e6:.0f} generation_ms={data.get('eval_duration',0)/1e6:.0f}")
    answer=data.get("message",{}).get("content","").strip()
    if not answer:raise RuntimeError("Ollama returned an empty response")
    return answer
