from software.app.robot import Robot
import time


def main():
    robot = Robot()

    print("FORWARD")
    robot.forward()
    time.sleep(2)

    print("STOP")
    robot.stop()


if __name__ == "__main__":
    main()