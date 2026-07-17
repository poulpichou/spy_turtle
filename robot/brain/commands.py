import time


class CommandManager:
    """
    Handles user commands.
    """

    def __init__(self, robot):
        self.robot = robot
        self.last_command = 0

        self.interaction_duration = 5.0

    def execute(self, command):
        self.last_command = time.time()

        print(f"[Command] {command}")

        if command == "forward":
            self.robot.forward()

        elif command == "backward":
            self.robot.backward()

        elif command == "left":
            self.robot.turn_left()

        elif command == "right":
            self.robot.turn_right()

        elif command == "stop":
            self.robot.stop()

        self.robot.set_emotion("happy")


    def update(self):
        pass


    def is_recent(self):
        return (
            time.time() - self.last_command
            < self.interaction_duration
        )