from robot.factory.robot_factory import RobotFactory
import time

robot=RobotFactory(simulation=False).create()

print("[TEST] status")
robot.shell.set_mode("status")
time.sleep(3)

print("[TEST] happy image")
robot.shell.set_mode("happy")
time.sleep(3)

print("[TEST] rocket image")
robot.shell.set_mode("rocket")
time.sleep(3)

print("[TEST] dance animation")
robot.shell.set_mode("dance")
time.sleep(5)

print("[TEST] smoke event")
robot.shell.trigger("smoke",5)

for _ in range(60):
    robot.update()
    time.sleep(0.1)

print("[TEST] finished")