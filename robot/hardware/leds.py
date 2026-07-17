class LEDController:
    def __init__(self):
        self.mode = "off"
        print("[LED] hardware ready")

    def set_mode(self, mode):
        self.mode = mode
        print(f"[LED] mode -> {mode}")

    def off(self): self.set_mode("off")
    def static(self, color): self.set_mode(f"static:{color}")
    def breathing(self, color): self.set_mode(f"breathing:{color}")
    def rainbow(self): self.set_mode("rainbow")
    def police(self): self.set_mode("police")
    def fire(self): self.set_mode("fire")
    def ocean(self): self.set_mode("ocean")