import json
import time
from threading import Lock,Thread
from urllib.request import Request,urlopen
from urllib.error import URLError
from robot.utils.logger import log
from robot.config import settings

# One Ollama runner: serialize requests so a background warmup never competes with a real question.
REQUEST_LOCK=Lock()
ROLLING_LOCK=Lock()
ROLLING_THREAD=None
ROLLING_VERSION=0

def _request(endpoint,payload):
    request=Request(settings.CHAT_OLLAMA_URL.rstrip("/")+endpoint,data=json.dumps(payload).encode("utf-8"),headers={"Content-Type":"application/json"},method="POST")
    with urlopen(request,timeout=settings.CHAT_TIMEOUT) as response:return json.load(response)

def _payload(messages,max_tokens):
    payload={"model":settings.CHAT_MODEL,"messages":messages,"stream":False,"options":{"num_predict":max_tokens,"temperature":settings.CHAT_TEMPERATURE,"num_ctx":settings.CHAT_CONTEXT_SIZE}}
    if settings.CHAT_KEEP_LOADED:payload["keep_alive"]=-1
    return payload

def _metrics(data):
    return f"prompt_tokens={data.get('prompt_eval_count','?')} generated_tokens={data.get('eval_count','?')} load_ms={data.get('load_duration',0)/1e6:.0f} prompt_ms={data.get('prompt_eval_duration',0)/1e6:.0f} generation_ms={data.get('eval_duration',0)/1e6:.0f}"

def preload():
    if not settings.CHAT_KEEP_LOADED:return
    started=time.monotonic()
    try:
        if settings.CHAT_STATIC_PROMPT_PRELOAD:
            from robot.brain import conversation
            from robot.speech import tts
            lang=tts.language()
            messages=[{"role":"system","content":conversation.system_prompt(lang)}]
            with REQUEST_LOCK:data=_request("/api/chat",_payload(messages,1))
            log.info(f"[LLM PRELOAD] mode=static-prefix language={lang} elapsed={time.monotonic()-started:.2f}s {_metrics(data)}")
        else:
            with REQUEST_LOCK:_request("/api/generate",{"model":settings.CHAT_MODEL,"keep_alive":-1})
            log.info(f"[LLM PRELOAD] mode=model-only elapsed={time.monotonic()-started:.2f}s")
    except Exception as error:log.warn(f"[LLM PRELOAD] failed: {error}")

def preload_async():
    if settings.CHAT_KEEP_LOADED:Thread(target=preload,name="ollama-preload",daemon=True).start()

def invalidate_rolling(reason="changed"):
    global ROLLING_VERSION
    with ROLLING_LOCK:
        ROLLING_VERSION+=1
        version=ROLLING_VERSION
    log.info(f"[LLM ROLLING] invalidated version={version} reason={reason}")

def _rolling_worker(messages,version,language,history_count):
    started=time.monotonic()
    try:
        # Do not queue behind a real conversation: the next question always has priority.
        if not REQUEST_LOCK.acquire(blocking=False):
            log.info(f"[LLM ROLLING] skipped version={version} reason=runner-busy");return
        try:
            with ROLLING_LOCK:stale=version!=ROLLING_VERSION
            if stale:
                log.info(f"[LLM ROLLING] skipped version={version} reason=stale");return
            # Experimental warmup: Ollama may reuse the matching prefix, but KV persistence is not guaranteed.
            data=_request("/api/chat",_payload(messages,1))
        finally:REQUEST_LOCK.release()
        with ROLLING_LOCK:stale=version!=ROLLING_VERSION
        log.info(f"[LLM ROLLING] status={'stale' if stale else 'done'} version={version} language={language} history_messages={history_count} elapsed={time.monotonic()-started:.2f}s {_metrics(data)}")
    except Exception as error:log.warn(f"[LLM ROLLING] status=error version={version} elapsed={time.monotonic()-started:.2f}s error={error}")

def prepare_rolling_async(messages,language,history_count):
    global ROLLING_THREAD,ROLLING_VERSION
    if not settings.CHAT_ROLLING_PRELOAD or not settings.CHAT_KEEP_LOADED:return
    with ROLLING_LOCK:
        ROLLING_VERSION+=1
        version=ROLLING_VERSION
        if ROLLING_THREAD and ROLLING_THREAD.is_alive():
            log.info(f"[LLM ROLLING] skipped version={version} reason=previous-running");return
        ROLLING_THREAD=Thread(target=_rolling_worker,args=(messages,version,language,history_count),name="ollama-rolling",daemon=True)
        ROLLING_THREAD.start()
    log.info(f"[LLM ROLLING] scheduled version={version} language={language} history_messages={history_count}")

def reply(messages):
    # Real requests win over waiting warmups; if warmup is already executing, report the wait explicitly.
    started=time.monotonic()
    with REQUEST_LOCK:
        waited=time.monotonic()-started
        try:data=_request("/api/chat",_payload(messages,settings.CHAT_MAX_TOKENS))
        except (URLError,TimeoutError,OSError) as error:raise RuntimeError(f"Ollama unavailable: {error}") from error
    elapsed=time.monotonic()-started
    log.info(f"[LLM TIMING] total={elapsed:.2f}s wait_ms={waited*1000:.0f} model={settings.CHAT_MODEL} {_metrics(data)}")
    answer=data.get("message",{}).get("content","").strip()
    if not answer:raise RuntimeError("Ollama returned an empty response")
    return answer
