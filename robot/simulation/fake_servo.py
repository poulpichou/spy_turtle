class FakeServo:
    def __init__(self):
        self.pan = 90
        self.tilt = 90
        print("[FakeServo] ready")

    def move_pan(self, angle):
        self.pan = angle
        print(f"[FakeServo] pan:{angle}")

    def move_tilt(self, angle):
        self.tilt = angle
        print(f"[FakeServo] tilt:{angle}")

    def look_left(self):
        self.move_pan(45)

    def look_right(self):
        self.move_pan(135)

    def look_up(self):
        self.move_tilt(45)

    def look_down(self):
        self.move_tilt(135)

    def center(self):
        self.pan = 90
        self.tilt = 90
        print("[FakeServo] center")