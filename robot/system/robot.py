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

        print("[Robot] initialized")

    def update(self):
        if self.brain: self.brain.update()
        if self.face: self.face.update()
        if self.shell: self.shell.update()

    def forward(self): self.motors.forward()

    def backward(self): self.motors.backward()

    def turn_left(self): self.motors.left()

    def turn_right(self): self.motors.right()

    def stop(self): self.motors.stop()

    def set_emotion(self,emotion):
        self.state.emotion=emotion
        self.face.play(emotion)

    def event(self,event):
        print(f"[Robot] event {event}")

        if event=="smoke":
            if self.shell: self.shell.trigger("smoke")

        elif event=="fire":
            if self.shell: self.shell.trigger("fire")

        elif event=="dance":
            if self.shell: self.shell.set_mode("video_2")

        elif event=="rocket":
            if self.shell: self.shell.set_mode("image_2")

    def shell_mode(self,mode):
        if self.shell: self.shell.set_mode(mode)

    def shell_event(self,event):
        if self.shell: self.shell.trigger(event)