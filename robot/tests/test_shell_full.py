from robot.factory.robot_factory import RobotFactory
import time

robot=RobotFactory(simulation=False).create()

robot.shell.set_mode("status")
time.sleep(3)

robot.shell.set_mode("image_1")
time.sleep(3)

robot.shell.set_mode("image_2")
time.sleep(3)

robot.shell.set_mode("log")
time.sleep(3)

robot.shell.trigger("smoke")
time.sleep(12)