from robot.config import settings
from robot.hardware.motor.motor import Motor
from robot.hardware.motor.tb6612 import TB6612Driver
from robot.utils.logger import log

class DifferentialDrive:
    def __init__(self):
        self.driver=TB6612Driver(
            standby_pin=settings.MOTOR_STBY_PIN,
            pwma_pin=settings.MOTOR_PWMA_PIN,
            ain1_pin=settings.MOTOR_AIN1_PIN,
            ain2_pin=settings.MOTOR_AIN2_PIN,
            pwmb_pin=settings.MOTOR_PWMB_PIN,
            bin1_pin=settings.MOTOR_BIN1_PIN,
            bin2_pin=settings.MOTOR_BIN2_PIN,
            pwm_frequency=settings.MOTOR_PWM_FREQUENCY
        )
        self.left_motor=Motor(self.driver,"A","left",settings.MOTOR_LEFT_INVERTED)
        self.right_motor=Motor(self.driver,"B","right",settings.MOTOR_RIGHT_INVERTED)
        self.left_speed=0.0
        self.right_speed=0.0
        self.motion="stop"
        log.info(f"[MOTORS] ready left_inverted={settings.MOTOR_LEFT_INVERTED} right_inverted={settings.MOTOR_RIGHT_INVERTED}")

    @staticmethod
    def normalize_speed(speed,default):
        speed=default if speed is None else float(speed)
        if speed==0:return 0.0
        sign=-1 if speed<0 else 1
        return sign*max(settings.MOTOR_MIN_SPEED,min(settings.MOTOR_MAX_SPEED,abs(speed)))

    def set_left_speed(self,speed):
        self.left_speed=max(-1.0,min(1.0,float(speed)))
        self.left_motor.set_speed(self.left_speed)

    def set_right_speed(self,speed):
        self.right_speed=max(-1.0,min(1.0,float(speed)))
        self.right_motor.set_speed(self.right_speed)

    def set_speeds(self,left,right):
        self.set_left_speed(left)
        self.set_right_speed(right)

    def forward(self,speed=None):
        speed=self.normalize_speed(speed,settings.MOTOR_DRIVE_SPEED)
        self.set_speeds(speed,speed)
        self.motion="forward"
        log.info(f"[MOTORS] forward speed={speed:.2f}")

    def backward(self,speed=None):
        speed=self.normalize_speed(speed,settings.MOTOR_DRIVE_SPEED)
        self.set_speeds(-speed,-speed)
        self.motion="backward"
        log.info(f"[MOTORS] backward speed={speed:.2f}")

    def left(self,speed=None):
        speed=self.normalize_speed(speed,settings.MOTOR_TURN_SPEED)
        self.set_speeds(-speed,speed)
        self.motion="left"
        log.info(f"[MOTORS] left speed={speed:.2f}")

    def right(self,speed=None):
        speed=self.normalize_speed(speed,settings.MOTOR_TURN_SPEED)
        self.set_speeds(speed,-speed)
        self.motion="right"
        log.info(f"[MOTORS] right speed={speed:.2f}")

    def turn_left(self,speed=None): self.left(speed)
    def turn_right(self,speed=None): self.right(speed)

    def stop(self):
        self.set_speeds(0,0)
        self.motion="stop"
        log.info("[MOTORS] stop")

    def status(self):
        return {"motion":self.motion,"left_speed":round(self.left_speed,3),"right_speed":round(self.right_speed,3),"left_inverted":settings.MOTOR_LEFT_INVERTED,"right_inverted":settings.MOTOR_RIGHT_INVERTED}

    def close(self):
        self.stop()
        self.driver.close()
