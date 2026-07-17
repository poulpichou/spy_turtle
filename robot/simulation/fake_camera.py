import time
import base64

class FakeCamera:
    def __init__(self):
        self.running = False
        print("[FakeCamera] ready")

    def start(self):
        self.running = True
        print("[FakeCamera] started")

    def stop(self):
        self.running = False
        print("[FakeCamera] stopped")

    def get_frame(self):
        if not self.running:
            return None

        frame = f"spy_turtle_fake_frame_{time.time()}"
        return base64.b64encode(frame.encode()).decode()