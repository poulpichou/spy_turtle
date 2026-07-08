class FakeOLED:
    def draw(self, frame):
        print("\n" * 2)
        print("┌──────────────┐")
        for line in frame:
            print("│" + line.ljust(14) + "│")
        print("└──────────────┘")