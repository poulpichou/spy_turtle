from robot.system.robot import Robot

from robot.face.face_controller import FaceController
from robot.face.eyes_renderer import EyesRenderer

from robot.simulation.fake_battery import FakeBattery
from robot.simulation.fake_camera import FakeCamera
from robot.simulation.fake_eyes_display import FakeEyesDisplay
from robot.simulation.fake_leds import FakeLEDController
from robot.simulation.fake_motor import FakeMotor
from robot.simulation.fake_speaker import FakeSpeaker
from robot.simulation.fake_servo import FakeServo

from robot.hardware.servo import ServoController
from robot.hardware.oled_display import OLEDDisplay
from robot.hardware.shell_screen_st7796 import ShellScreenST7796
from robot.shell.shell_controller import ShellController


class RobotFactory:
    def __init__(self,simulation=True): self.simulation=simulation

    def create(self):
        if self.simulation: return self.create_simulation()
        return self.create_hardware()

    def create_simulation(self):
        motors=FakeMotor()
        leds=FakeLEDController()
        camera=FakeCamera()
        battery=FakeBattery()
        speaker=FakeSpeaker()
        servo=FakeServo()

        left_display=FakeEyesDisplay("left")
        right_display=FakeEyesDisplay("right")

        eyes_renderer=EyesRenderer(left_display,right_display)
        face=FaceController(eyes_renderer)

        return Robot(
            motors=motors,
            face=face,
            leds=leds,
            camera=camera,
            battery=battery,
            speaker=speaker,
            servo=servo
        )

    def create_hardware(self):
        motors=FakeMotor()
        leds=FakeLEDController()
        camera=FakeCamera()
        battery=FakeBattery()
        speaker=FakeSpeaker()
        servo=ServoController()

        left_display=OLEDDisplay(0x3C,"left")
        right_display=OLEDDisplay(0x3C,"right")

        eyes_renderer=EyesRenderer(left_display,right_display)
        face=FaceController(eyes_renderer)

        shell_screen=ShellScreenST7796()
        shell=ShellController(shell_screen)

        robot=Robot(
            motors=motors,
            face=face,
            leds=leds,
            camera=camera,
            battery=battery,
            speaker=speaker,
            servo=servo,
            shell=shell
        )

        shell.set_robot(robot)

        return robot