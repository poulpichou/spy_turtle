from software.hardware.motor import MotorDriver


class Robot:
    def __init__(self):
        self.motors = MotorDriver()

    def forward(self):
        self.motors.forward()

    def backward(self):
        self.motors.backward()

    def turn_left(self):
        self.motors.turn_left()

    def turn_right(self):
        self.motors.turn_right()

    def stop(self):
        self.motors.stop()