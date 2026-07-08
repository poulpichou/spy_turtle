from robot.system.robot import Robot

from robot.simulation.fake_motor import FakeMotor
from robot.simulation.fake_oled import FakeOLED
from robot.simulation.fake_face import FakeFace


class RobotFactory:
    """
    Creates a complete robot instance.

    This is the only place that knows
    which hardware implementation is used.
    """

    @staticmethod
    def create(simulation=True):

        if simulation:
            print("[Factory] Creating simulation robot")

            oled = FakeOLED()
            face = FakeFace(oled)
            motors = FakeMotor()

        else:
            print("[Factory] Creating hardware robot")

            from robot.hardware.motor import MotorDriver
            from robot.face.eyes import Eyes
            from robot.face.mouth import Mouth

            motors = MotorDriver()

            oled = None
            face = None

            # Hardware face implementation
            # will be completed later

        return Robot(
            motors=motors,
            face=face
        )