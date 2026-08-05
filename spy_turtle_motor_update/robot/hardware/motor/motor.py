class Motor:
    def __init__(self,driver,channel,name,inverted=False):
        self.driver=driver
        self.channel=channel
        self.name=name
        self.inverted=inverted
        self.speed=0.0

    def set_speed(self,speed):
        speed=max(-1.0,min(1.0,float(speed)))
        self.speed=speed
        self.driver.set_channel(self.channel,-speed if self.inverted else speed)

    def stop(self): self.set_speed(0)
