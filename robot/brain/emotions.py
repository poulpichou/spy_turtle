import time


class EmotionManager:
    """
    Controls Spy Turtle emotional state.

    The emotion manager updates the robot state
    and applies the corresponding face expression.
    """

    def __init__(self, robot):
        self.robot = robot
        self.last_change = time.time()

    def set_emotion(self, emotion):
        self.robot.state.emotion = emotion
        self.last_change = time.time()

        print(f"[Emotion] {emotion}")

        self.robot.face.set_expression(emotion)

    def update(self):
        """
        Future emotion evolution logic.

        For now emotions stay stable.
        """
        pass