class Speaker:
    def __init__(self):
        self.volume=100

    def play(self,text):
        print(f"[Speaker] play:{text}")

    def stop(self): pass

    def set_volume(self,volume): self.volume=volume