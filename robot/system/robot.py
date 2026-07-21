from robot.system.state import TurtleState

class Robot:
    def __init__(self,motors,face,leds,camera,battery,speaker,servo,shell=None):
        self.motors=motors
        self.face=face
        self.leds=leds
        self.camera=camera
        self.battery=battery
        self.speaker=speaker
        self.servo=servo
        self.shell=shell
        self.state=TurtleState()
        self.brain=None
        if self.face:self.face.play("neutral")
        print("[Robot] initialized")

    def update(self):
        if self.brain:self.brain.update()
        if self.face and self.face.update():
            self.state.emotion="neutral"
            self.state.face_event_until=0.0
        if self.shell:
            self.shell.update()
            if hasattr(self.shell.screen,"update"):self.shell.screen.update()

    def forward(self): self.motors.forward()
    def backward(self): self.motors.backward()
    def turn_left(self): self.motors.left()
    def turn_right(self): self.motors.right()
    def stop(self): self.motors.stop()

    def set_emotion(self,emotion):
        self.state.emotion=emotion
        if self.face:self.face.play(emotion)

    def shell_mode(self,mode):
        if self.shell:self.shell.set_mode(mode)

    def shell_event(self,event):
        if self.shell:self.shell.trigger(event)
