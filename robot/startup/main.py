import time

from robot.factory.robot_factory import RobotFactory


def main():

    print("[Startup] Starting Spy Turtle")

    robot = RobotFactory.create(
        simulation=True
    )

    print("Spy Turtle online")

    robot.set_emotion("happy")


    while True:

        robot.update()

        time.sleep(0.1)


if __name__ == "__main__":
    main()