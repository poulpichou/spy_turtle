import time

DEBUG=True

class log:
    @staticmethod
    def _print(level,msg): print(f"{time.strftime('%H:%M:%S')} [{level}] {msg}")

    @staticmethod
    def info(msg): log._print("INFO",msg)

    @staticmethod
    def warn(msg): log._print("WARN",msg)

    @staticmethod
    def error(msg): log._print("ERROR",msg)

    @staticmethod
    def debug(msg):
        if DEBUG: log._print("DEBUG",msg)