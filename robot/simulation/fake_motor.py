class FakeMotor:
    def __init__(self):
        self.left_speed = 0
        self.right_speed = 0
        print("[FakeMotor] ready")

    def set_left_speed(self, speed):
        self.left_speed = speed
        print(f"[FakeMotor] left speed -> {speed}")

    def set_right_speed(self, speed):
        self.right_speed = speed
        print(f"[FakeMotor] right speed -> {speed}")

    def forward(self, speed=0.6):
        self.set_left_speed(speed)
        self.set_right_speed(speed)
        print("[FakeMotor] forward")

    def backward(self, speed=0.6):
        self.set_left_speed(-speed)
        self.set_right_speed(-speed)
        print("[FakeMotor] backward")

    def turn_left(self, speed=0.6):
        self.set_left_speed(-speed)
        self.set_right_speed(speed)
        print("[FakeMotor] turn left")

    def turn_right(self, speed=0.6):
        self.set_left_speed(speed)
        self.set_right_speed(-speed)
        print("[FakeMotor] turn right")

    def stop(self):
        self.set_left_speed(0)
        self.set_right_speed(0)
        print("[FakeMotor] stop")