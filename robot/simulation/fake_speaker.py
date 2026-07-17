class FakeSpeaker:
    def __init__(self):
        self.volume = 100
        print("[FakeSpeaker] ready")

    def play(self, text):
        print(f"[FakeSpeaker] play:{text}")

    def stop(self):
        print("[FakeSpeaker] stop")

    def set_volume(self, volume):
        self.volume = volume
        print(f"[FakeSpeaker] volume:{volume}")