from robot.factory.robot_factory import RobotFactory
import time

robot=RobotFactory(simulation=False).create()
robot.face.happy()

while True:
    robot.update()
    time.sleep(0.1)