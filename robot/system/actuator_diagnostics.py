import time
from collections import deque
from robot.system.runtime import get_robot
from robot.utils.logger import log
events=deque(maxlen=120)
last_tick=0
ticks=0
def record(kind,message):
 events.append({"at":round(time.time(),2),"kind":kind,"message":str(message)})
 log.info(f"[DIAG {kind}] {message}")
def tick():
 global ticks,last_tick
 ticks+=1;last_tick=time.monotonic()
def snapshot():
 r=get_robot()
 d={"ticks":ticks,"loop_age_s":round(time.monotonic()-last_tick,2) if last_tick else None,"events":list(events)}
 if r:
  d["idle_mode"]=r.power.idle_mode;d["motion"]=r.state.motion
  for name,component in (("servo",r.servo),("motors",r.motors)):
   try:d[name]=component.status() if component else None
   except Exception as e:d[name]={"error":str(e)}
 return d
