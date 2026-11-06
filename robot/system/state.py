import time
from dataclasses import dataclass,field

@dataclass
class TurtleState:
    battery:dict=field(default_factory=lambda:{
        'level':None,'status':'unknown','voltage_v':None,'current_a':None,'power_w':None,
        'cells_mv':[],'remaining_capacity':None,'charging':None,'usb_connected':None,
        'updated_at':None,'error':None
    })
    vision:dict=field(default_factory=lambda:{'detected_current':[],'detected_recent':[]})
    emotion:str='neutral'
    mood:str='neutral'
    mood_variant:str='neutral_1'
    mood_context_fr:str=''
    mood_context_en:str=''
    mood_deadline_monotonic:float=0.0
    led_mode:str='off'
    camera_on:bool=False
    motion:str='stop'
    x:float=0.0
    y:float=0.0
    angle:float=0.0
    shell_mode:str='status'
    shell_event:str|None=None
    started_at:float=field(default_factory=time.time)
    last_interaction_at:float=field(default_factory=time.time)
    last_interaction_type:str='startup'
    interaction_count:int=0
    face_event_until:float=0.0
    sleeping_until:float=0.0

    def touch(self,interaction_type):
        self.last_interaction_at=time.time()
        self.last_interaction_type=str(interaction_type)
        self.interaction_count+=1

    def idle_seconds(self): return max(0.0,time.time()-self.last_interaction_at)

    def to_dict(self):
        now=time.time()
        return {
            'battery':self.battery.copy(),
            'vision':{'detected_current':[f.copy() for f in self.vision['detected_current']],'detected_recent':[p.copy() for p in self.vision['detected_recent']]},
            'brain':{'emotion':self.emotion,'mood':self.mood,'mood_variant':self.mood_variant,'mood_context_fr':self.mood_context_fr,'mood_context_en':self.mood_context_en,'mood_remaining_seconds':round(max(0,self.mood_deadline_monotonic-time.monotonic()),1),'idle_seconds':self.idle_seconds(),'last_interaction_type':self.last_interaction_type,'interaction_count':self.interaction_count,'face_event_until':self.face_event_until,'sleeping_until':self.sleeping_until},
            'camera':{'on':self.camera_on},
            'motion':{'state':self.motion,'x':self.x,'y':self.y,'angle':self.angle},
            'shell':{'mode':self.shell_mode,'event':self.shell_event},
            'leds':{'mode':self.led_mode},
            'system':{'started_at':self.started_at,'now':now,'uptime_seconds':max(0.0,now-self.started_at)}
        }
