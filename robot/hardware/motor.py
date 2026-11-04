"""TB6612FNG differential drive with optional single-channel encoder balancing."""
import time
from threading import RLock
from gpiozero import PWMOutputDevice, DigitalOutputDevice, DigitalInputDevice
from robot.config import settings


def clamp(value,low,high): return max(low,min(high,value))


class DifferentialDrive:
    def __init__(self):
        self._lock=RLock()
        self._counts=[0,0]
        self._encoders=[]
        self._mode="stop"
        self._base=0.0
        self._correction=0.0
        self._last_sample=time.monotonic()
        self._last_counts=(0,0)
        self._last_log=0.0
        self._encoder_ready=False
        self.pwma=PWMOutputDevice(settings.MOTOR_PWMA_PIN,frequency=settings.MOTOR_PWM_FREQUENCY,initial_value=0)
        self.ain1=DigitalOutputDevice(settings.MOTOR_AIN1_PIN,initial_value=False)
        self.ain2=DigitalOutputDevice(settings.MOTOR_AIN2_PIN,initial_value=False)
        self.pwmb=PWMOutputDevice(settings.MOTOR_PWMB_PIN,frequency=settings.MOTOR_PWM_FREQUENCY,initial_value=0)
        self.bin1=DigitalOutputDevice(settings.MOTOR_BIN1_PIN,initial_value=False)
        self.bin2=DigitalOutputDevice(settings.MOTOR_BIN2_PIN,initial_value=False)
        self.stby=DigitalOutputDevice(settings.MOTOR_STBY_PIN,initial_value=True)
        if settings.MOTOR_ENCODERS_ENABLED:
            try:
                left=DigitalInputDevice(settings.MOTOR_LEFT_ENCODER_A_PIN,pull_up=settings.MOTOR_ENCODER_PULL_UP)
                self._encoders.append(left)
                right=DigitalInputDevice(settings.MOTOR_RIGHT_ENCODER_A_PIN,pull_up=settings.MOTOR_ENCODER_PULL_UP)
                self._encoders.append(right)
                left.when_activated=self._left_tick
                right.when_activated=self._right_tick
                self._encoder_ready=True
            except Exception as error:
                print(f"[MOTOR] Encoder initialization failed; open-loop fallback: {error}")
                for encoder in self._encoders:encoder.close()
                self._encoders.clear()
        print(f"[MOTOR] ready; encoders={self._encoder_ready}; correction={self._enabled()}")

    def _left_tick(self):
        with self._lock:self._counts[0]+=1

    def _right_tick(self):
        with self._lock:self._counts[1]+=1

    def _enabled(self):return self._encoder_ready and settings.MOTOR_ENCODER_CORRECTION_ENABLED

    def encoder_counts(self):
        with self._lock:return tuple(self._counts)

    def _reset(self):
        self._correction=0.0
        self._last_counts=tuple(self._counts)
        self._last_sample=time.monotonic()

    def _apply(self,left,right):
        if settings.MOTOR_LEFT_INVERTED:left=-left
        if settings.MOTOR_RIGHT_INVERTED:right=-right
        self._drive_motor(left,self.pwma,self.ain1,self.ain2)
        self._drive_motor(right,self.pwmb,self.bin1,self.bin2)

    @staticmethod
    def _drive_motor(speed,pwm,in1,in2):
        speed=clamp(float(speed),-1.0,1.0)
        if speed>0:
            in1.on();in2.off();pwm.value=speed
        elif speed<0:
            in1.off();in2.on();pwm.value=-speed
        else:
            pwm.value=0;in1.off();in2.off()

    def _command(self,mode,speed):
        with self._lock:
            default=settings.MOTOR_TURN_SPEED if mode in ("left","right") else settings.MOTOR_DRIVE_SPEED
            speed=clamp(abs(float(default if speed is None else speed)),0.0,1.0)
            if mode!=self._mode or speed!=self._base:self._reset()
            self._mode=mode;self._base=speed
            if mode=="forward":self._apply(speed+self._correction,speed-self._correction)
            elif mode=="backward":self._apply(-speed-self._correction,-speed+self._correction)
            elif mode=="left":self._apply(-speed,speed)
            elif mode=="right":self._apply(speed,-speed)
            else:self._apply(0,0)

    def forward(self,speed=None):self._command("forward",speed)
    def backward(self,speed=None):self._command("backward",speed)
    def turn_left(self,speed=None):self._command("left",speed)
    def turn_right(self,speed=None):self._command("right",speed)
    def left(self,speed=None):self.turn_left(speed)
    def right(self,speed=None):self.turn_right(speed)
    def stop(self):self._command("stop",0)

    def set_left_speed(self,speed):
        with self._lock:
            self._mode="manual";self._reset()
            if settings.MOTOR_LEFT_INVERTED:speed=-speed
            self._drive_motor(speed,self.pwma,self.ain1,self.ain2)

    def set_right_speed(self,speed):
        with self._lock:
            self._mode="manual";self._reset()
            if settings.MOTOR_RIGHT_INVERTED:speed=-speed
            self._drive_motor(speed,self.pwmb,self.bin1,self.bin2)

    def update(self):
        if not self._enabled():return
        with self._lock:
            if self._mode not in ("forward","backward") or self._base<=0:return
            now=time.monotonic()
            dt=now-self._last_sample
            if dt<max(0.02,float(settings.MOTOR_ENCODER_CORRECTION_INTERVAL)):return
            counts=tuple(self._counts)
            left=counts[0]-self._last_counts[0]
            right=counts[1]-self._last_counts[1]
            self._last_counts=counts;self._last_sample=now
            if left+right<max(1,int(settings.MOTOR_ENCODER_CORRECTION_MIN_PULSES)):
                self._correction=0.0
            else:
                # Positive error = right wheel faster => speed up left / slow down right.
                error=(right-left)/max(left+right,1)
                target=clamp(float(settings.MOTOR_ENCODER_CORRECTION_KP)*error,-float(settings.MOTOR_ENCODER_CORRECTION_MAX),float(settings.MOTOR_ENCODER_CORRECTION_MAX))
                # Positive correction raises left PWM and lowers right PWM.
                self._correction=target
            direction=1 if self._mode=="forward" else -1
            left_pwm=clamp(self._base+self._correction,0,1)
            right_pwm=clamp(self._base-self._correction,0,1)
            self._apply(direction*left_pwm,direction*right_pwm)
            log_interval=float(getattr(settings,"MOTOR_ENCODER_CORRECTION_LOG_INTERVAL",2.0))
            if log_interval>0 and now-self._last_log>=log_interval:
                self._last_log=now
                print(f"[MOTOR CTRL] {self._mode} pulses L={left} R={right} dt={dt:.2f}s pwm L={left_pwm:.3f} R={right_pwm:.3f} correction={self._correction:+.3f}")

    def close(self):
        self.stop()
        for encoder in self._encoders:encoder.close()
        self.stby.off()
        for device in (self.pwma,self.pwmb,self.ain1,self.ain2,self.bin1,self.bin2,self.stby):device.close()


MotorDriver=DifferentialDrive
