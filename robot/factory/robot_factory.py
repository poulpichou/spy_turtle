from robot.system.robot import Robot
from robot.brain.brain import Brain

from robot.simulation.fake_motor import FakeMotor
from robot.simulation.fake_leds import FakeLEDController
from robot.simulation.fake_camera import FakeCamera
from robot.simulation.fake_battery import FakeBattery
from robot.simulation.fake_speaker import FakeSpeaker
from robot.simulation.fake_servo import FakeServo
from robot.simulation.fake_face import FakeFace

class RobotFactory:
    def __init__(self, simulation=True):
        self.simulation = simulation

    def create(self):
        if self.simulation:
            motors = FakeMotor()
            leds = FakeLEDController()
            camera = FakeCamera()
            battery = FakeBattery()
            speaker = FakeSpeaker()
            servo = FakeServo()
            face = FakeFace()
        else:
            raise NotImplementedError("Hardware mode not implemented yet")

        robot = Robot(motors, face, leds, camera, battery, speaker, servo)
        robot.brain = Brain(robot)
        return robot