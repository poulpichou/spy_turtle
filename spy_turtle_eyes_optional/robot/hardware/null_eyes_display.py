class NullEyesDisplay:
    """No-op eye display used when OLED eyes are disabled or unavailable."""
    def __init__(self,name="eye"): self.name=name
    def show(self,bitmap): pass
    def clear(self): pass
