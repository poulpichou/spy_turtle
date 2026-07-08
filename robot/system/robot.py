from robot.system.state import TurtleState
from robot.brain.brain import Brain


class Robot:
    def __init__(self, motors, face):
        self.state = TurtleState()

        self.motors = motors
        self.face = face

        self.brain = Brain(self)

        print("[Robot] initialized")

    def update(self):
        self.brain.update()

    def set_emotion(self, emotion):
        self.brain.emotions.set_emotion(emotion)

    def execute_command(self, command):
        self.brain.commands.execute(command)

    def forward(self):
        self.motors.forward()
        self.state.moving = "forward"

    def backward(self):
        self.motors.backward()
        self.state.moving = "backward"

    def turn_left(self):
        self.motors.turn_left()
        self.state.moving = "turn_left"

    def turn_right(self):
        self.motors.turn_right()
        self.state.moving = "turn_right"

    def stop(self):
        self.motors.stop()
        self.state.moving = "stopped"