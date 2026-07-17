from robot.system.state import TurtleState

class Robot:
    def __init__(self, motors, face, leds, camera, battery, speaker, servo):
        self.motors = motors
        self.face = face
        self.leds = leds
        self.camera = camera
        self.battery = battery
        self.speaker = speaker
        self.servo = servo
        self.state = TurtleState()
        self.brain = None
        print("[Robot] initialized")

    def update(self):
        if self.brain:
            self.brain.update()

        if self.face:
            self.face.update()