import time
import re
from threading import RLock
from collections import deque

DEBUG=True

class log:
    _history=deque(maxlen=100)
    _lock=RLock()
    _line_pattern=re.compile(r"^\d{2}:\d{2}:\d{2} (DEBUG|INFO |WARN |ERROR) - ")

    @staticmethod
    def _print(level,msg):
        line=f"{time.strftime('%H:%M:%S')} {level:<5} - {msg}"
        with log._lock:
            print(line,flush=True)
            log._history.append(line)

    @staticmethod
    def info(msg): log._print("INFO",msg)

    @staticmethod
    def warn(msg): log._print("WARN",msg)

    @staticmethod
    def error(msg): log._print("ERROR",msg)

    @staticmethod
    def debug(msg):
        if DEBUG:log._print("DEBUG",msg)

    @staticmethod
    def tail(count=10,level="DEBUG"):
        levels={"DEBUG":0,"INFO":1,"WARN":2,"WARNING":2,"ERROR":3}
        threshold=levels.get(level.upper(),0)
        with log._lock:
            return tuple(line for line in log._history if (match:=log._line_pattern.match(line)) and levels[match.group(1).strip()]>=threshold)[-count:]

    @staticmethod
    def history():
        with log._lock:return tuple(log._history)

    @staticmethod
    def clear():
        with log._lock:log._history.clear()