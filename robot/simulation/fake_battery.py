class FakeBattery:
    def __init__(self):
        self.level = 100
        self.charging = False
        print("[FakeBattery] ready")

    def get_level(self):
        return self.level

    def is_charging(self):
        return self.charging

    def drain(self, amount=1):
        self.level = max(0, self.level - amount)

    def charge(self):
        self.charging = True
        self.level = min(100, self.level + 1)

    def stop_charging(self):
        self.charging = False