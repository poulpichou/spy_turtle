from dataclasses import dataclass

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
    shell_event:str=None