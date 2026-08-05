from gpiozero import DigitalOutputDevice,PWMOutputDevice

from robot.utils.logger import log

class TB6612Driver:
    def __init__(self,standby_pin,pwma_pin,ain1_pin,ain2_pin,pwmb_pin,bin1_pin,bin2_pin,pwm_frequency=1000):
        self.standby=DigitalOutputDevice(standby_pin,initial_value=False)
        self.ain1=DigitalOutputDevice(ain1_pin,initial_value=False)
        self.ain2=DigitalOutputDevice(ain2_pin,initial_value=False)
        self.pwma=PWMOutputDevice(pwma_pin,frequency=pwm_frequency,initial_value=0)
        self.bin1=DigitalOutputDevice(bin1_pin,initial_value=False)
        self.bin2=DigitalOutputDevice(bin2_pin,initial_value=False)
        self.pwmb=PWMOutputDevice(pwmb_pin,frequency=pwm_frequency,initial_value=0)
        self._closed=False
        self.standby.on()
        log.info(f"[TB6612] ready STBY={standby_pin} A=({pwma_pin},{ain1_pin},{ain2_pin}) B=({pwmb_pin},{bin1_pin},{bin2_pin})")

    def set_channel(self,channel,speed):
        if self._closed:raise RuntimeError("TB6612 driver is closed")
        speed=max(-1.0,min(1.0,float(speed)))
        if channel=="A":self._set(self.ain1,self.ain2,self.pwma,speed)
        elif channel=="B":self._set(self.bin1,self.bin2,self.pwmb,speed)
        else:raise ValueError(f"Unknown TB6612 channel: {channel}")

    @staticmethod
    def _set(in1,in2,pwm,speed):
        if speed>0:
            in1.on()
            in2.off()
            pwm.value=speed
        elif speed<0:
            in1.off()
            in2.on()
            pwm.value=-speed
        else:
            pwm.value=0
            in1.off()
            in2.off()

    def stop(self):
        if self._closed:return
        self.set_channel("A",0)
        self.set_channel("B",0)

    def sleep(self):
        if self._closed:return
        self.stop()
        self.standby.off()

    def wake(self):
        if self._closed:raise RuntimeError("TB6612 driver is closed")
        self.standby.on()

    def close(self):
        if self._closed:return
        self.sleep()
        self.pwma.close()
        self.pwmb.close()
        self.ain1.close()
        self.ain2.close()
        self.bin1.close()
        self.bin2.close()
        self.standby.close()
        self._closed=True
        log.info("[TB6612] closed")
