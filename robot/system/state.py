from dataclasses import dataclass, field

@dataclass
class TurtleState:
    battery: float = 87.0
    emotion: str = "happy"
    led_mode: str = "idle"
    camera_on: bool = True
    x: float = 0.0
    y: float = 0.0
    angle: float = 0.0

STATE = TurtleState()