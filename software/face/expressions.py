class Expressions:
    def __init__(self, eyes, mouth):
        self.eyes = eyes
        self.mouth = mouth

    def happy(self):
        self.eyes.happy()
        self.mouth.smile()

    def neutral(self):
        self.eyes.open()
        self.mouth.neutral()

    def sad(self):
        self.eyes.sad()
        self.mouth.sad()

    def surprised(self):
        self.eyes.surprised()
        self.mouth.surprised()

    def sleepy(self):
        self.eyes.sleepy()
        self.mouth.sleepy()

    def angry(self):
        self.eyes.angry()
        self.mouth.sad()