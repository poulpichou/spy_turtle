class Face:
    """
    Abstract face interface.

    The Brain interacts with this interface only.
    The implementation can be a real OLED face or a simulation.
    """

    def blink(self):
        pass

    def look_left(self):
        pass

    def look_right(self):
        pass

    def set_expression(self, expression):
        pass