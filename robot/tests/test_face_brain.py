import time
from robot.factory.robot_factory import RobotFactory
from robot.brain.brain import Brain

robot=RobotFactory(simulation=False).create()
robot.brain=Brain(robot)

robot.face.neutral()

while True:
    robot.update()
    time.sleep(0.5)