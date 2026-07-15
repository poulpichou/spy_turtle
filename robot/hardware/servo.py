from gpiozero import Servo


class ServoController:
    """
    Real servo controller.

    Controls the camera rotation servo.
    """

    def __init__(self, pin=18):
        self.servo = Servo(pin)

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