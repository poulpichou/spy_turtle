import time
import base64


class Camera:
    def __init__(self):
        self.running = False
        print("[Camera] initialized (simulation mode)")

    def start(self):
        self.running = True
        print("[Camera] stream started")

    def stop(self):
        self.running = False
        print("[Camera] stream stopped")

    def get_frame(self):
        """
        Returns a fake JPEG-like frame (base64 string)
        In real mode → PiCamera JPEG bytes
        """
        if not self.running:
            return None

        # Fake “image payload”
        fake_frame = f"spy_turtle_frame_{time.time()}"

        encoded = base64.b64encode(fake_frame.encode()).decode()
        return encoded