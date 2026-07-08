from dataclasses import dataclass


@dataclass
class TurtleState:
    battery: float = 100.0
    emotion: str = "neutral"
    led_mode: str = "idle"
    camera_on: bool = False

    x: float = 0.0
    y: float = 0.0
    angle: float = 0.0

    connected: bool = True
    moving: str = "stopped"