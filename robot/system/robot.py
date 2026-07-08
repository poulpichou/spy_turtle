from robot.system.state import TurtleState
from robot.brain.brain import Brain


class Robot:
    def __init__(self, motors, face):
        self.state = TurtleState()
        self.motors = motors
        self.face = face
        self.brain = Brain(self)

    def update(self):
        self.brain.update()

    def forward(self):
        self.motors.forward()

    def stop(self):
        self.motors.stop()