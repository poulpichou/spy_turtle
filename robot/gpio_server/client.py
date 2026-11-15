import json
import socket
import threading
from pathlib import Path

SOCKET=Path('/tmp/spyturtle-gpio.sock')

class GPIOUnavailable(RuntimeError):pass

class GPIOClient:
    def __init__(self,path=SOCKET):self.path=str(path);self.lock=threading.RLock()
    def call(self,component,method,*args,timeout=0.7):
        request={'component':component,'method':method,'args':list(args)}
        with self.lock:
            try:
                with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM) as sock:
                    sock.settimeout(timeout);sock.connect(self.path)
                    sock.sendall((json.dumps(request,separators=(',',':'))+'\n').encode())
                    with sock.makefile('rb') as stream:raw=stream.readline(262144)
                if not raw:raise GPIOUnavailable('GPIO server closed connection')
                response=json.loads(raw)
                if not response.get('ok'):raise GPIOUnavailable(response.get('error','GPIO command failed'))
                return response.get('result')
            except (OSError,ValueError,TimeoutError) as error:raise GPIOUnavailable(f'GPIO server unavailable: {error}') from error

client=GPIOClient()
