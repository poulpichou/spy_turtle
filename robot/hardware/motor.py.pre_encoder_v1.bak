from gpiozero import PWMOutputDevice, DigitalOutputDevice


class MotorDriver:
    def __init__(self):
        self.pwma = PWMOutputDevice(12)
        self.ain1 = DigitalOutputDevice(23)
        self.ain2 = DigitalOutputDevice(24)

        self.pwmb = PWMOutputDevice(13)
        self.bin1 = DigitalOutputDevice(27)
        self.bin2 = DigitalOutputDevice(22)

        self.stby = DigitalOutputDevice(17)
        self.stby.on()

        print("[MotorDriver] hardware ready")

    def set_left_speed(self, speed):
        self._drive_motor(speed, self.pwma, self.ain1, self.ain2)

    def set_right_speed(self, speed):
        self._drive_motor(speed, self.pwmb, self.bin1, self.bin2)

    def forward(self, speed=0.6):
        self.set_left_speed(speed)
        self.set_right_speed(speed)

    def backward(self, speed=0.6):
        self.set_left_speed(-speed)
        self.set_right_speed(-speed)

    def turn_left(self, speed=0.6):
        self.set_left_speed(-speed)
        self.set_right_speed(speed)

    def turn_right(self, speed=0.6):
        self.set_left_speed(speed)
        self.set_right_speed(-speed)

    def stop(self):
        self.set_left_speed(0)
        self.set_right_speed(0)

    def _drive_motor(self, speed, pwm, in1, in2):
        speed = max(-1.0, min(1.0, speed))

        if speed > 0:
            in1.on()
            in2.off()
            pwm.value = speed
        elif speed < 0:
            in1.off()
            in2.on()
            pwm.value = abs(speed)
        else:
            in1.off()
            in2.off()
            pwm.value = 0