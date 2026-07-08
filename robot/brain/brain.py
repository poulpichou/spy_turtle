from robot.brain.idle import IdleBehaviour
from robot.brain.emotions import EmotionManager
from robot.brain.commands import CommandManager
from robot.brain.planner import Planner


class Brain:
    """
    Main robot behaviour controller.

    The Brain coordinates behaviour modules.
    """

    def __init__(self, robot):
        self.robot = robot

        self.commands = CommandManager(robot)
        self.emotions = EmotionManager(robot)
        self.idle = IdleBehaviour(robot)

        self.planner = Planner(robot)

        print("[Brain] initialized")

    def update(self):

        self.commands.update()
        self.emotions.update()

        priority = self.planner.get_priority()

        if priority <= 10:
            self.idle.update()