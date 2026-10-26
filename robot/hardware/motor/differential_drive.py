import threading
import time

from robot.config import settings
from robot.hardware.motor.motor import Motor
from robot.hardware.motor.motor_encoder import MotorEncoder
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
        self.left_encoder=None
        self.right_encoder=None
        self.left_speed=0.0
        self.right_speed=0.0
        self.target_left_speed=0.0
        self.target_right_speed=0.0
        self.motion="stop"
        self.speed_multiplier=1.0
        self._correction=0.0
        self._correction_stop=threading.Event()
        self._correction_thread=None
        if settings.MOTOR_ENCODERS_ENABLED:self._create_encoders()
        if settings.MOTOR_ENCODER_CORRECTION_ENABLED and self.left_encoder and self.right_encoder:self._start_correction()
        log.info(f"[MOTORS] ready left_inverted={settings.MOTOR_LEFT_INVERTED} right_inverted={settings.MOTOR_RIGHT_INVERTED} encoders={settings.MOTOR_ENCODERS_ENABLED} correction={settings.MOTOR_ENCODER_CORRECTION_ENABLED}")

    def _create_encoders(self):
        self.left_encoder=MotorEncoder(
            settings.MOTOR_LEFT_ENCODER_A_PIN,settings.MOTOR_LEFT_ENCODER_B_PIN,"left",
            settings.MOTOR_LEFT_ENCODER_INVERTED,settings.MOTOR_ENCODER_PULL_UP,
            settings.MOTOR_ENCODER_PULSES_PER_REV,settings.MOTOR_WHEEL_DIAMETER_MM
        )
        self.right_encoder=MotorEncoder(
            settings.MOTOR_RIGHT_ENCODER_A_PIN,settings.MOTOR_RIGHT_ENCODER_B_PIN,"right",
            settings.MOTOR_RIGHT_ENCODER_INVERTED,settings.MOTOR_ENCODER_PULL_UP,
            settings.MOTOR_ENCODER_PULSES_PER_REV,settings.MOTOR_WHEEL_DIAMETER_MM
        )
        log.info(f"[MOTORS] encoders ready left=A{settings.MOTOR_LEFT_ENCODER_A_PIN} right=A{settings.MOTOR_RIGHT_ENCODER_A_PIN} single_channel={settings.MOTOR_LEFT_ENCODER_B_PIN is None and settings.MOTOR_RIGHT_ENCODER_B_PIN is None}")

    def _start_correction(self):
        self._correction_thread=threading.Thread(target=self._correction_loop,name="motor-encoder-correction",daemon=True)
        self._correction_thread.start()
        log.info(f"[MOTORS] encoder correction ready interval={settings.MOTOR_ENCODER_CORRECTION_INTERVAL:.3f}s kp={settings.MOTOR_ENCODER_CORRECTION_KP:.4f} max={settings.MOTOR_ENCODER_CORRECTION_MAX:.3f}")

    def _correction_loop(self):
        previous_left=self.left_encoder.get_ticks()
        previous_right=self.right_encoder.get_ticks()
        while not self._correction_stop.wait(settings.MOTOR_ENCODER_CORRECTION_INTERVAL):
            left=self.left_encoder.get_ticks();right=self.right_encoder.get_ticks()
            left_delta=abs(left-previous_left);right_delta=abs(right-previous_right)
            previous_left=left;previous_right=right
            if self.motion not in ("forward","backward") or not self.target_left_speed or not self.target_right_speed:
                self._correction=0.0
                continue
            total=left_delta+right_delta
            if total<settings.MOTOR_ENCODER_CORRECTION_MIN_PULSES:continue
            error=(right_delta-left_delta)/max(1,total)
            self._correction=max(-settings.MOTOR_ENCODER_CORRECTION_MAX,min(settings.MOTOR_ENCODER_CORRECTION_MAX,error*settings.MOTOR_ENCODER_CORRECTION_KP))
            left_sign=1 if self.target_left_speed>0 else -1
            right_sign=1 if self.target_right_speed>0 else -1
            left=left_sign*max(0.0,min(1.0,abs(self.target_left_speed)+self._correction))
            right=right_sign*max(0.0,min(1.0,abs(self.target_right_speed)-self._correction))
            self._apply_speeds(left,right)

    @staticmethod
    def normalize_speed(speed,default):
        speed=default if speed is None else float(speed)
        if speed==0:return 0.0
        sign=-1 if speed<0 else 1
        return sign*max(settings.MOTOR_MIN_SPEED,min(settings.MOTOR_MAX_SPEED,abs(speed)))

    def _apply_speeds(self,left,right):
        self.left_speed=max(-1.0,min(1.0,float(left)))
        self.right_speed=max(-1.0,min(1.0,float(right)))
        self.left_motor.set_speed(self.left_speed)
        self.right_motor.set_speed(self.right_speed)

    def set_left_speed(self,speed):
        self.left_speed=max(-1.0,min(1.0,float(speed)))
        self.left_motor.set_speed(self.left_speed)

    def set_right_speed(self,speed):
        self.right_speed=max(-1.0,min(1.0,float(speed)))
        self.right_motor.set_speed(self.right_speed)

    def set_speeds(self,left,right):
        self.target_left_speed=max(-1.0,min(1.0,float(left)))
        self.target_right_speed=max(-1.0,min(1.0,float(right)))
        self._correction=0.0
        self._apply_speeds(self.target_left_speed,self.target_right_speed)

    def set_speed_percent(self,percent):
        self.speed_multiplier=max(1.0,min(3.0,float(percent)/100.0))
        return round(self.speed_multiplier*100)

    def get_speed_percent(self): return round(self.speed_multiplier*100)

    def forward(self,speed=None):
        speed=self.normalize_speed(speed,settings.MOTOR_DRIVE_SPEED*self.speed_multiplier)
        self.motion="forward"
        self.set_speeds(speed,speed)
        log.info(f"[MOTORS] forward speed={speed:.2f}")

    def backward(self,speed=None):
        speed=self.normalize_speed(speed,settings.MOTOR_DRIVE_SPEED*self.speed_multiplier)
        self.motion="backward"
        self.set_speeds(-speed,-speed)
        log.info(f"[MOTORS] backward speed={speed:.2f}")

    def left(self,speed=None):
        speed=self.normalize_speed(speed,settings.MOTOR_TURN_SPEED*self.speed_multiplier)
        self.motion="left"
        self.set_speeds(-speed,speed)
        log.info(f"[MOTORS] left speed={speed:.2f}")

    def right(self,speed=None):
        speed=self.normalize_speed(speed,settings.MOTOR_TURN_SPEED*self.speed_multiplier)
        self.motion="right"
        self.set_speeds(speed,-speed)
        log.info(f"[MOTORS] right speed={speed:.2f}")

    def turn_left(self,speed=None):self.left(speed)
    def turn_right(self,speed=None):self.right(speed)

    def stop(self):
        self.motion="stop"
        self.set_speeds(0,0)
        self.speed_multiplier=1.0
        log.info("[MOTORS] stop")

    def reset_encoders(self):
        if self.left_encoder:self.left_encoder.reset()
        if self.right_encoder:self.right_encoder.reset()

    def status(self):
        return {
            "motion":self.motion,
            "left_speed":round(self.left_speed,3),
            "right_speed":round(self.right_speed,3),
            "left_inverted":settings.MOTOR_LEFT_INVERTED,
            "right_inverted":settings.MOTOR_RIGHT_INVERTED,
            "encoders":{
                "enabled":settings.MOTOR_ENCODERS_ENABLED,
                "correction_enabled":settings.MOTOR_ENCODER_CORRECTION_ENABLED,
                "correction":round(self._correction,4),
                "left":self.left_encoder.status() if self.left_encoder else None,
                "right":self.right_encoder.status() if self.right_encoder else None
            }
        }

    def close(self):
        self._correction_stop.set()
        if self._correction_thread and self._correction_thread.is_alive():self._correction_thread.join(timeout=1.0)
        self.stop()
        if self.left_encoder:self.left_encoder.close()
        if self.right_encoder:self.right_encoder.close()
        self.driver.close()
