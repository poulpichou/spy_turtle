from robot.config import motors as config
from robot.hardware.motor.motor import Motor
from robot.hardware.motor.tb6612 import TB6612Driver
from robot.utils.logger import log

class DifferentialDrive:
    def __init__(self):
        self.driver=TB6612Driver(
            standby_pin=config.STBY_PIN,
            pwma_pin=config.PWMA_PIN,
            ain1_pin=config.AIN1_PIN,
            ain2_pin=config.AIN2_PIN,
            pwmb_pin=config.PWMB_PIN,
            bin1_pin=config.BIN1_PIN,
            bin2_pin=config.BIN2_PIN,
            pwm_frequency=config.PWM_FREQUENCY
        )
        self.left_motor=Motor(self.driver,"A","left",config.LEFT_INVERTED)
        self.right_motor=Motor(self.driver,"B","right",config.RIGHT_INVERTED)
        self.left_speed=0.0
        self.right_speed=0.0
        self.motion="stop"
        log.info(f"[MOTORS] ready left_inverted={config.LEFT_INVERTED} right_inverted={config.RIGHT_INVERTED}")

    @staticmethod
    def normalize_speed(speed,default):
        speed=default if speed is None else float(speed)
        if speed==0:return 0.0
        sign=-1 if speed<0 else 1
        return sign*max(config.MIN_SPEED,min(config.MAX_SPEED,abs(speed)))

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
        speed=self.normalize_speed(speed,config.DRIVE_SPEED)
        self.set_speeds(speed,speed)
        self.motion="forward"
        log.info(f"[MOTORS] forward speed={speed:.2f}")

    def backward(self,speed=None):
        speed=self.normalize_speed(speed,config.DRIVE_SPEED)
        self.set_speeds(-speed,-speed)
        self.motion="backward"
        log.info(f"[MOTORS] backward speed={speed:.2f}")

    def left(self,speed=None):
        speed=self.normalize_speed(speed,config.TURN_SPEED)
        self.set_speeds(-speed,speed)
        self.motion="left"
        log.info(f"[MOTORS] left speed={speed:.2f}")

    def right(self,speed=None):
        speed=self.normalize_speed(speed,config.TURN_SPEED)
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
        return {
            "motion":self.motion,
            "left_speed":round(self.left_speed,3),
            "right_speed":round(self.right_speed,3),
            "left_inverted":config.LEFT_INVERTED,
            "right_inverted":config.RIGHT_INVERTED
        }

    def close(self):
        self.stop()
        self.driver.close()
