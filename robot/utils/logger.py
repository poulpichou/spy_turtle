import time
from collections import deque

DEBUG = True

class log:
    _history = deque(maxlen=100)

    @staticmethod
    def _print(level, msg):
        line = f"{time.strftime('%H:%M:%S')} [{level}] {msg}"
        print(line)
        log._history.append(line)

    @staticmethod
    def info(msg): log._print("INFO", msg)

    @staticmethod
    def warn(msg): log._print("WARN", msg)

    @staticmethod
    def error(msg): log._print("ERROR", msg)

    @staticmethod
    def debug(msg):
        if DEBUG: log._print("DEBUG", msg)

    @staticmethod
    def tail(count=10): return tuple(log._history)[-count:]

    @staticmethod
    def history(): return tuple(log._history)

    @staticmethod
    def clear(): log._history.clear()