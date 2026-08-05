import time
from gpiozero import DigitalOutputDevice,PWMOutputDevice

STBY_PIN=5
AIN1_PIN=6
AIN2_PIN=13
PWMA_PIN=12

def main():
    standby=DigitalOutputDevice(STBY_PIN,initial_value=False)
    in1=DigitalOutputDevice(AIN1_PIN,initial_value=False)
    in2=DigitalOutputDevice(AIN2_PIN,initial_value=False)
    pwm=PWMOutputDevice(PWMA_PIN,frequency=1000,initial_value=0)

    try:
        print("Enabling driver")
        standby.on()

        print("Forward 40%")
        in1.on()
        in2.off()
        pwm.value=0.4
        time.sleep(1)

        print("Stop")
        pwm.value=0
        in1.off()
        in2.off()
        time.sleep(1)

        print("Backward 40%")
        in1.off()
        in2.on()
        pwm.value=0.4
        time.sleep(1)

        print("Stop")
        pwm.value=0
        in1.off()
        in2.off()
    finally:
        pwm.value=0
        standby.off()
        pwm.close()
        in1.close()
        in2.close()
        standby.close()
        print("Done")

if __name__=="__main__":
    main()