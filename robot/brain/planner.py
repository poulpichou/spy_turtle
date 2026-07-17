class Planner:
    """
    Decides which behaviour is allowed to run.

    Higher priority behaviours block lower ones.
    """

    def __init__(self, robot):
        self.robot = robot

    def get_priority(self):
        """
        Returns current highest priority.
        """

        # User interaction
        if self.robot.brain.commands.is_recent():
            return 50

        # Future:
        # battery critical -> 100
        # emergency -> 100

        return 10