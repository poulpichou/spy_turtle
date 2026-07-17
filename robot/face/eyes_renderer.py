class EyesRenderer:
    def __init__(self, left_display, right_display):
        self.left_display = left_display
        self.right_display = right_display

        print("[EyesRenderer] ready")

    def show(self, left_eye, right_eye):
        self.left_display.show(left_eye)
        self.right_display.show(right_eye)