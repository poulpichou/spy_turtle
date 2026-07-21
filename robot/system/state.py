import time
from dataclasses import dataclass,field

@dataclass
class TurtleState:
    battery:float=87.0
    emotion:str="neutral"
    led_mode:str="off"
    camera_on:bool=False
    motion:str="stop"
    x:float=0.0
    y:float=0.0
    angle:float=0.0
    shell_mode:str="status"
    shell_event:str|None=None
    started_at:float=field(default_factory=time.time)
    last_interaction_at:float=field(default_factory=time.time)
    last_interaction_type:str="startup"
    interaction_count:int=0
    face_event_until:float=0.0
    sleeping_until:float=0.0

    def touch(self,interaction_type):
        self.last_interaction_at=time.time()
        self.last_interaction_type=str(interaction_type)
        self.interaction_count+=1

    def idle_seconds(self): return max(0.0,time.time()-self.last_interaction_at)

    def to_dict(self):
        data=self.__dict__.copy()
        data["now"]=time.time()
        data["uptime_seconds"]=max(0.0,time.time()-self.started_at)
        data["idle_seconds"]=self.idle_seconds()
        return data
