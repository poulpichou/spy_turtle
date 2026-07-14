import time
import random


class SimulationEngine:
    """
    Generates random simulated robot behaviour.

    The engine only sends sequences to the face controller.
    Timing and rendering are handled by FaceEngine.
    """

    def __init__(self, face):
        self.face = face
        self.running = True

    def blink(self):
        print("[Simulation] blink")
        self.face.play("blink")

    def yawn(self):
        print("[Simulation] yawn")
        self.face.play("yawn")

    def random_expression(self):
        choices = [
            "happy",
            "sad",
            "surprised",
            "angry",
            "sleepy"
        ]

        expression = random.choice(choices)

        print(f"[Simulation] expression: {expression}")

        self.face.play(expression)

    def idle_loop(self):
        actions = [
            self.blink,
            self.yawn,
            self.random_expression
        ]

        print("Starting simulation idle loop. Press Ctrl+C to stop.")

        while self.running:
            action = random.choice(actions)
            action()

            print("[Simulation] idle action")

            time.sleep(random.uniform(1.5, 3.0))