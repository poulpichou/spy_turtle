import time
from threading import RLock
from robot.config import settings
from robot.hardware.motor.motor import Motor
from robot.hardware.motor.motor_encoder import MotorEncoder
from robot.hardware.motor.tb6612 import TB6612Driver
from robot.utils.logger import log

def clamp(value,low,high):return max(low,min(high,float(value)))

class DifferentialDrive:
    def __init__(self):
        self._lock=RLock()
        self.driver=TB6612Driver(settings.MOTOR_STBY_PIN,settings.MOTOR_PWMA_PIN,settings.MOTOR_AIN1_PIN,settings.MOTOR_AIN2_PIN,settings.MOTOR_PWMB_PIN,settings.MOTOR_BIN1_PIN,settings.MOTOR_BIN2_PIN,settings.MOTOR_PWM_FREQUENCY)
        self.left_motor=Motor(self.driver,"A","left",settings.MOTOR_LEFT_INVERTED)
        self.right_motor=Motor(self.driver,"B","right",settings.MOTOR_RIGHT_INVERTED)
        self.left_encoder=None;self.right_encoder=None
        self.left_speed=0.0;self.right_speed=0.0
        self.target_left_speed=0.0;self.target_right_speed=0.0
        self.motion="stop";self.speed_multiplier=1.0;self._correction=0.0
        self._last_sample=time.monotonic();self._last_counts=(0,0);self._last_log=0.0
        if settings.MOTOR_ENCODERS_ENABLED:
            try:self._create_encoders()
            except Exception:
                if self.left_encoder:self.left_encoder.close()
                if self.right_encoder:self.right_encoder.close()
                self.left_encoder=None;self.right_encoder=None
                log.error("[MOTORS] encoder initialization failed; correction disabled")
        log.info(f"[MOTORS] ready encoders={self._encoders_ready()} correction={self._enabled()} (main loop)")

    def _create_encoders(self):
        self.left_encoder=MotorEncoder(settings.MOTOR_LEFT_ENCODER_A_PIN,settings.MOTOR_LEFT_ENCODER_B_PIN,"left",settings.MOTOR_LEFT_ENCODER_INVERTED,settings.MOTOR_ENCODER_PULL_UP,settings.MOTOR_ENCODER_PULSES_PER_REV,settings.MOTOR_WHEEL_DIAMETER_MM)
        self.right_encoder=MotorEncoder(settings.MOTOR_RIGHT_ENCODER_A_PIN,settings.MOTOR_RIGHT_ENCODER_B_PIN,"right",settings.MOTOR_RIGHT_ENCODER_INVERTED,settings.MOTOR_ENCODER_PULL_UP,settings.MOTOR_ENCODER_PULSES_PER_REV,settings.MOTOR_WHEEL_DIAMETER_MM)

    def _encoders_ready(self):return self.left_encoder is not None and self.right_encoder is not None
    def _enabled(self):return self._encoders_ready() and settings.MOTOR_ENCODER_CORRECTION_ENABLED

    @staticmethod
    def normalize_speed(speed,default):
        speed=float(default if speed is None else speed)
        if speed==0:return 0.0
        return (1 if speed>0 else -1)*clamp(abs(speed),settings.MOTOR_MIN_SPEED,settings.MOTOR_MAX_SPEED)

    def _counts(self):return (self.left_encoder.get_ticks(),self.right_encoder.get_ticks()) if self._encoders_ready() else (0,0)

    def _reset_correction(self):
        self._correction=0.0
        self._last_counts=self._counts()
        self._last_sample=time.monotonic()

    def _apply_speeds(self,left,right):
        self.left_speed=clamp(left,-1,1);self.right_speed=clamp(right,-1,1)
        self.left_motor.set_speed(self.left_speed);self.right_motor.set_speed(self.right_speed)

    def _correction_eligible(self,motion,left,right):
        if not self._enabled() or motion not in ("forward","backward","joystick"):return False
        if left*right<=0:return False
        low=min(abs(left),abs(right));high=max(abs(left),abs(right))
        return high>=settings.MOTOR_MIN_SPEED and low/high>=0.65

    def _corrected_speeds(self):
        left=self.target_left_speed;right=self.target_right_speed
        if not self._correction_eligible(self.motion,left,right):return left,right
        sign=1 if left>0 else -1
        return sign*clamp(abs(left)+self._correction,0,1),sign*clamp(abs(right)-self._correction,0,1)

    def _set_motion(self,motion,left,right):
        with self._lock:
            left=clamp(left,-1,1);right=clamp(right,-1,1)
            changed=(motion!=self.motion or left!=self.target_left_speed or right!=self.target_right_speed)
            was_eligible=self._correction_eligible(self.motion,self.target_left_speed,self.target_right_speed)
            eligible=self._correction_eligible(motion,left,right)
            direction_changed=(left>0)!=(self.target_left_speed>0) or (right>0)!=(self.target_right_speed>0)
            if eligible and was_eligible and not direction_changed:
                # Keep encoder sampling across joystick heartbeat and small steering changes.
                # Reset after a significant change in requested wheel-speed ratio.
                old_ratio=abs(self.target_left_speed)/(abs(self.target_left_speed)+abs(self.target_right_speed))
                new_ratio=abs(left)/(abs(left)+abs(right))
                reset=abs(new_ratio-old_ratio)>0.10
            else:reset=True
            self.motion=motion;self.target_left_speed=left;self.target_right_speed=right
            if reset:self._reset_correction()
            self._apply_speeds(*self._corrected_speeds())
            if changed:log.info(f"[MOTORS] {motion} left={left:.2f} right={right:.2f}")

    def set_left_speed(self,speed):
        with self._lock:self._set_motion("manual",speed,self.target_right_speed)

    def set_right_speed(self,speed):
        with self._lock:self._set_motion("manual",self.target_left_speed,speed)

    def set_speeds(self,left,right):self._set_motion("manual",left,right)
    def joystick(self,left,right):self._set_motion("joystick",left,right)
    def set_speed_percent(self,percent):
        with self._lock:self.speed_multiplier=clamp(float(percent)/100.0,1.0,3.0)
        return self.get_speed_percent()
    def get_speed_percent(self):return round(self.speed_multiplier*100)

    def forward(self,speed=None):
        speed=abs(self.normalize_speed(speed,settings.MOTOR_DRIVE_SPEED*self.speed_multiplier))
        self._set_motion("forward",speed,speed)

    def backward(self,speed=None):
        speed=abs(self.normalize_speed(speed,settings.MOTOR_DRIVE_SPEED*self.speed_multiplier))
        self._set_motion("backward",-speed,-speed)

    def left(self,speed=None):
        speed=abs(self.normalize_speed(speed,settings.MOTOR_TURN_SPEED*self.speed_multiplier))
        self._set_motion("left",-speed,speed)

    def right(self,speed=None):
        speed=abs(self.normalize_speed(speed,settings.MOTOR_TURN_SPEED*self.speed_multiplier))
        self._set_motion("right",speed,-speed)

    def turn_left(self,speed=None):self.left(speed)
    def turn_right(self,speed=None):self.right(speed)

    def stop(self):
        with self._lock:
            self._set_motion("stop",0,0)
            self.speed_multiplier=1.0

    def update(self):
        if not self._enabled():return
        with self._lock:
            left_target=self.target_left_speed;right_target=self.target_right_speed
            if not self._correction_eligible(self.motion,left_target,right_target):return
            now=time.monotonic();dt=now-self._last_sample
            if dt<max(0.02,float(settings.MOTOR_ENCODER_CORRECTION_INTERVAL)):return
            counts=self._counts()
            left=abs(counts[0]-self._last_counts[0]);right=abs(counts[1]-self._last_counts[1])
            self._last_counts=counts;self._last_sample=now
            total=left+right
            if total>=max(1,int(settings.MOTOR_ENCODER_CORRECTION_MIN_PULSES)):
                # Compare measured wheel proportions with requested wheel proportions.
                # Positive error means right wheel is faster than requested.
                target_total=abs(left_target)+abs(right_target)
                expected_right=abs(right_target)/target_total
                error=2*(right/total-expected_right)
                self._correction=clamp(error*settings.MOTOR_ENCODER_CORRECTION_KP,-settings.MOTOR_ENCODER_CORRECTION_MAX,settings.MOTOR_ENCODER_CORRECTION_MAX)
            else:self._correction=0.0
            self._apply_speeds(*self._corrected_speeds())
            interval=float(getattr(settings,"MOTOR_ENCODER_CORRECTION_LOG_INTERVAL",2.0))
            if interval>0 and now-self._last_log>=interval:
                self._last_log=now
                log.info(f"[MOTOR CTRL] {self.motion} pulses L={left} R={right} dt={dt:.2f}s pwm L={self.left_speed:.3f} R={self.right_speed:.3f} correction={self._correction:+.3f}")

    def reset_encoders(self):
        with self._lock:
            if self.left_encoder:self.left_encoder.reset()
            if self.right_encoder:self.right_encoder.reset()
            self._reset_correction()

    def status(self):
        with self._lock:
            return {"motion":self.motion,"left_speed":round(self.left_speed,3),"right_speed":round(self.right_speed,3),"left_inverted":settings.MOTOR_LEFT_INVERTED,"right_inverted":settings.MOTOR_RIGHT_INVERTED,"encoders":{"enabled":self._encoders_ready(),"correction_enabled":self._enabled(),"correction":round(self._correction,4),"left":self.left_encoder.status() if self.left_encoder else None,"right":self.right_encoder.status() if self.right_encoder else None}}

    def close(self):
        with self._lock:
            self.stop()
            if self.left_encoder:self.left_encoder.close()
            if self.right_encoder:self.right_encoder.close()
            self.driver.close()
