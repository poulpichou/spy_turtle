import gc
import threading
import time
from robot.utils.logger import log

class RobotResetManager:
    def __init__(self):
        self._lock=threading.Lock();self._pending=None;self._resetting=False
    def request(self,timeout=45):
        with self._lock:
            if self._pending is not None or self._resetting:raise RuntimeError('Robot reset already in progress')
            request={'event':threading.Event(),'result':None};self._pending=request
        if not request['event'].wait(timeout):raise TimeoutError('Robot reset still in progress; check logs')
        return request['result']
    def pending(self):
        with self._lock:
            request=self._pending
            if request is None:return None
            self._pending=None;self._resetting=True
            return request
    def finish(self,request,result):
        with self._lock:
            self._resetting=False;request['result']=result;request['event'].set()
    def is_resetting(self):
        with self._lock:return self._resetting or self._pending is not None

reset_manager=RobotResetManager()

def close_robot(robot):
    errors={}
    if robot is None:return errors
    # Stop actuators first. Never restart the previous motion.
    try:
        if robot.motors:robot.motors.stop()
    except Exception as error:errors['motors_stop']=str(error)
    for name in ('motors','servo','camera','thermal_camera','speaker','distance_sensor','environment_sensor','battery','leds'):
        component=getattr(robot,name,None)
        if component is None:continue
        method=getattr(component,'close',None)
        if method is None and name=='speaker':method=getattr(component,'stop',None)
        if method is None:continue
        try:method()
        except Exception as error:errors[name]=str(error);log.error(f'[RESET] close {name}: {error}')
    if robot.face:
        renderer=getattr(getattr(robot.face,'engine',None),'renderer',None)
        if renderer:
            for name in ('left_display','right_display'):
                display=getattr(renderer,name,None)
                if display and hasattr(display,'close'):
                    try:display.close()
                    except Exception as error:errors[name]=str(error)
    if robot.shell:
        try:robot.shell.close()
        except Exception as error:errors['shell']=str(error)
        screen=getattr(robot.shell,'screen',None)
        if screen and hasattr(screen,'display'):
            try:screen.display.close()
            except Exception as error:errors['shell_display']=str(error)
    return errors

def reconstruct(old):
    from robot.api.actions import disarm_motion
    from robot.config import settings
    from robot.factory.robot_factory import RobotFactory
    from robot.system.runtime import set_robot
    disarm_motion()
    set_robot(None)
    errors=close_robot(old)
    if errors:
        # Do not claim a full reset if a resource may still be owned.
        log.error(f'[RESET] incomplete cleanup: {errors}')
        return None,{'ok':False,'phase':'close','errors':errors}
    del old
    gc.collect()
    # Deliberately do not force dlclose on Python extension modules.
    new=RobotFactory(simulation=settings.SIMULATION).create()
    set_robot(new)
    return new,{'ok':True,'phase':'ready','native_reload':'not_attempted','message':'Robot reconstructed; FastAPI process preserved'}
