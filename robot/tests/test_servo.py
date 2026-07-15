import time

from robot.hardware.servo import ServoController


def main():
    servo = ServoController()

    print("Center")
    servo.center()
    time.sleep(2)

    print("Left")
    servo.look_left()
    time.sleep(2)

    print("Right")
    servo.look_right()
    time.sleep(2)

    print("Center")
    servo.center()
    time.sleep(2)

    servo.detach()

    print("Done")


if __name__ == "__main__":
    main()