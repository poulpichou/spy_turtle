from gpiozero import Servo
from robot.config.settings import SERVO_CAMERA_PIN

class ServoController:
    def __init__(self,pin=SERVO_CAMERA_PIN):
        self.servo=Servo(pin)
        print(f"[Servo] GPIO{pin} ready")

    def center(self):
        print("[Servo] center")
        self.servo.mid()

    def look_left(self):
        print("[Servo] left")
        self.servo.min()

    def look_right(self):
        print("[Servo] right")
        self.servo.max()

    def detach(self):
        self.servo.detach()