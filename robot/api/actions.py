def move_forward(robot):
    robot.execute_command("forward")


def move_backward(robot):
    robot.execute_command("backward")


def turn_left(robot):
    robot.execute_command("left")


def turn_right(robot):
    robot.execute_command("right")


def stop(robot):
    robot.execute_command("stop")


def set_emotion(robot, emotion):
    robot.set_emotion(emotion)


def set_led(robot, mode):
    robot.state.led_mode = mode