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
from robot.simulation.fake_thermal_camera import FakeThermalCamera
from robot.hardware.power_leds import LEDController
from robot.hardware.servo import ServoController
from robot.hardware.oled_display import OLEDDisplay
from robot.hardware.shell_screen_st7796 import ShellScreenST7796
from robot.hardware.battery import Battery
from robot.hardware.camera import Camera
from robot.hardware.thermal_camera import ThermalCamera
from robot.hardware.speaker import Speaker
from robot.hardware.motor import DifferentialDrive
from robot.shell.power_shell_controller import ShellController
from robot.shell.ui.shell_ui import ShellUI
from robot.brain.brain import Brain
from robot.config import settings
from robot.utils.logger import log

class RobotFactory:
    def __init__(self,simulation=True): self.simulation=simulation
    def create(self): return self.create_simulation() if self.simulation else self.create_hardware()
    def create_simulation(self):
        motors=FakeMotor();leds=FakeLEDController();camera=FakeCamera()
        thermal_camera=FakeThermalCamera() if settings.THERMAL_CAMERA_ENABLED else None
        battery=FakeBattery();speaker=FakeSpeaker();servo=FakeServo()
        left_display=FakeEyesDisplay("left");right_display=FakeEyesDisplay("right")
        eyes_renderer=EyesRenderer(left_display,right_display);face=FaceController(eyes_renderer,leds)
        robot=Robot(motors=motors,face=face,leds=leds,camera=camera,thermal_camera=thermal_camera,battery=battery,speaker=speaker,servo=servo)
        robot.brain=Brain(robot)
        return robot
    def create_hardware(self):
        motors=DifferentialDrive();leds=LEDController();camera=Camera();thermal_camera=None
        if settings.THERMAL_CAMERA_ENABLED:
            try:thermal_camera=ThermalCamera()
            except Exception as error:log.error(f"[THERMAL] initialization failed, RGB fallback remains active: {error}")
        speaker=Speaker();servo=ServoController();battery=Battery()
        left_display=OLEDDisplay(settings.OLED_LEFT_ADDRESS,"left");right_display=OLEDDisplay(settings.OLED_RIGHT_ADDRESS,"right")
        eyes_renderer=EyesRenderer(left_display,right_display);face=FaceController(eyes_renderer,leds)
        shell_screen=ShellScreenST7796();shell_ui=ShellUI(shell_screen.display);shell=ShellController(shell_ui)
        robot=Robot(motors=motors,face=face,leds=leds,camera=camera,thermal_camera=thermal_camera,battery=battery,speaker=speaker,servo=servo,shell=shell)
        shell.set_robot(robot);robot.brain=Brain(robot)
        return robot
