import time

from robot.factory.robot_factory import RobotFactory


def main():
    robot = RobotFactory(simulation=True).create()

    robot.face.neutral()

    print("[Test] Robot loop running")

    while True:
        robot.update()
        time.sleep(0.02)


if __name__ == "__main__":
    main()