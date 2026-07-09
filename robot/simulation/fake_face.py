class FakeFace:
    def __init__(self):
        print("[FakeFace] ready")
        self.expression = "neutral"
        self.direction = "center"

    def set_expression(self, expression):
        self.expression = expression
        print(f"[FakeFace] expression:{expression}")

    def blink(self):
        print("[FakeFace] blink")

    def yawn(self):
        print("[FakeFace] yawn")

    def happy(self):
        self.set_expression("happy")

    def sad(self):
        self.set_expression("sad")

    def sleepy(self):
        self.set_expression("sleepy")

    def surprised(self):
        self.set_expression("surprised")

    def angry(self):
        self.set_expression("angry")

    def look_left(self):
        self.direction = "left"
        print("[FakeFace] look:left")

    def look_right(self):
        self.direction = "right"
        print("[FakeFace] look:right")

    def look_center(self):
        self.direction = "center"
        print("[FakeFace] look:center")