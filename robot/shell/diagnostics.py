# [SHELL DIAG PATCH]
import time
from collections import deque
from threading import RLock
from robot.utils.logger import log
_events=deque(maxlen=250)
_lock=RLock()
_counters={"render":0,"spi":0,"blocked":0,"errors":0}
_last={}

def trace(stage,**data):
    event={"at":round(time.time(),3),"stage":stage,**data}
    with _lock:
        _events.append(event)
        if stage in _counters:_counters[stage]+=1
        _last.update({"stage":stage,"at":event["at"],**data})
    if stage not in ("render","spi") or _counters.get(stage,0)%100==0:log.debug(f"[SHELL DEBUG] {stage} {data}")

def snapshot(robot):
    shell=getattr(robot,"shell",None)
    power=getattr(robot,"power",None)
    screen=getattr(shell,"screen",None)
    display=getattr(screen,"display",None)
    with _lock:events=list(_events);counters=dict(_counters);last=dict(_last)
    return {"power":{"idle_mode":getattr(power,"idle_mode",None),"back_screen":power.data.get("back_screen") if power else None},"shell":{"present":shell is not None,"enabled":getattr(shell,"enabled",None),"active_mode":getattr(shell,"active_mode",None),"view":type(shell.view).__name__ if shell and shell.view else None,"expires_at":getattr(shell,"expires_at",None),"state_shell_mode":getattr(robot.state,"shell_mode",None),"screen_present":screen is not None,"display_present":display is not None},"counters":counters,"last":last,"events":events}
