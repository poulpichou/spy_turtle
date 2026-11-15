import json
import os
import signal
import socketserver
import threading
import time
from pathlib import Path
from robot.gpio_server.client import SOCKET
from robot.utils.logger import log

MOTOR_METHODS={'forward','backward','left','right','turn_left','turn_right','stop','joystick','set_speeds','set_left_speed','set_right_speed','set_speed_percent','get_speed_percent','reset_encoders','reset_pwm','set_correction_enabled','status'}
SERVO_METHODS={'look_left','look_right','look_up','look_down','center','detach','reset_gpio','status','diagnostic'}
MOVING={'forward','backward','left','right','turn_left','turn_right','joystick','set_speeds','set_left_speed','set_right_speed'}

class Handler(socketserver.StreamRequestHandler):
    def handle(self):
        try:
            raw=self.rfile.readline(8192)
            if not raw or len(raw)>=8192:raise ValueError('Request missing or too large')
            request=json.loads(raw)
            component=request['component'];method=request['method'];args=request.get('args',[])
            allowed=MOTOR_METHODS if component=='motors' else SERVO_METHODS if component=='servo' else set()
            if method not in allowed or not isinstance(args,list):raise ValueError('Unsupported GPIO operation')
            with self.server.hardware_lock:
                device=self.server.motors if component=='motors' else self.server.servo
                result=getattr(device,method)(*args)
                if component=='motors':
                    if method in MOVING:self.server.last_motion=time.monotonic()
                    elif method=='stop':self.server.last_motion=0.0
            reply={'ok':True,'result':result}
        except Exception as error:
            log.error(f'[GPIO SERVER] request failed: {type(error).__name__}: {error}')
            reply={'ok':False,'error':f'{type(error).__name__}: {error}'}
        try:self.wfile.write((json.dumps(reply,default=str,separators=(',',':'))+'\n').encode())
        except (OSError,BrokenPipeError):pass

class Server(socketserver.ThreadingMixIn,socketserver.UnixStreamServer):
    daemon_threads=True;allow_reuse_address=False
    def __init__(self,path,motors,servo):
        self.motors=motors;self.servo=servo;self.hardware_lock=threading.RLock();self.last_motion=0.0;self.running=True
        super().__init__(str(path),Handler)

def main():
    # Import native GPIO modules only inside this process.
    from robot.hardware.motor import DifferentialDrive
    from robot.hardware.servo import ServoController
    if SOCKET.exists():
        import socket
        try:
            with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM) as sock:
                sock.settimeout(0.3);sock.connect(str(SOCKET))
            raise SystemExit('GPIO server already running')
        except (ConnectionRefusedError,FileNotFoundError):SOCKET.unlink(missing_ok=True)
    motors=None;servo=None;server=None
    try:
        motors=DifferentialDrive();servo=ServoController()
        server=Server(SOCKET,motors,servo);os.chmod(SOCKET,0o600)
        def terminate(*_):
            server.running=False
            threading.Thread(target=server.shutdown,daemon=True).start()
        signal.signal(signal.SIGTERM,terminate);signal.signal(signal.SIGINT,terminate)
        def loop():
            while server.running:
                with server.hardware_lock:
                    try:
                        if server.last_motion and time.monotonic()-server.last_motion>1.5:
                            motors.stop();server.last_motion=0.0;log.warn('[GPIO SAFETY] motor command timeout -> stop')
                        motors.update();servo.update()
                    except Exception as error:log.error(f'[GPIO SERVER] update failed: {error}')
                time.sleep(0.02)
        worker=threading.Thread(target=loop,name='gpio-update',daemon=True);worker.start()
        log.info(f'[GPIO SERVER] ready pid={os.getpid()} socket={SOCKET}')
        server.serve_forever(poll_interval=0.1)
    finally:
        if server:server.running=False;server.server_close()
        if motors:
            try:motors.stop();motors.close()
            except Exception as error:log.error(f'[GPIO SERVER] motors cleanup: {error}')
        if servo:
            try:servo.close()
            except Exception as error:log.error(f'[GPIO SERVER] servo cleanup: {error}')
        SOCKET.unlink(missing_ok=True)
        log.info('[GPIO SERVER] stopped')

if __name__=='__main__':main()
