class FakeMotor:
    def __init__(self):
        self.state = "stopped"
        print("[FakeMotor] ready")

    def forward(self, speed=0.6):
        self.state = "forward"
        print("[Motor] forward")

    def backward(self, speed=0.6):
        self.state = "backward"
        print("[Motor] backward")

    def turn_left(self, speed=0.6):
        self.state = "left"
        print("[Motor] left")

    def turn_right(self, speed=0.6):
        self.state = "right"
        print("[Motor] right")

    def stop(self):
        self.state = "stopped"
        print("[Motor] stop")