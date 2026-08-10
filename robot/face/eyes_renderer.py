class EyesRenderer:
    def __init__(self,left_display,right_display):
        self.left_display=left_display
        self.right_display=right_display
        self.enabled=True
        print("[EyesRenderer] ready")

    def set_enabled(self,enabled):
        self.enabled=bool(enabled)
        if not self.enabled:
            if hasattr(self.left_display,"clear"):self.left_display.clear()
            if hasattr(self.right_display,"clear"):self.right_display.clear()
        return self.enabled

    def show(self,left_eye,right_eye):
        if not self.enabled:return
        self.left_display.show(left_eye)
        self.right_display.show(right_eye)
