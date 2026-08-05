import argparse
import time

from robot.hardware.motor import DifferentialDrive

def run(channel,speed,duration):
    drive=DifferentialDrive()
    try:
        if channel in ("a","both"):
            print(f"Channel A forward {speed:.0%}")
            drive.set_left_speed(speed)
            time.sleep(duration)
            drive.stop()
            time.sleep(1)
            print(f"Channel A backward {speed:.0%}")
            drive.set_left_speed(-speed)
            time.sleep(duration)
            drive.stop()
        if channel=="both":time.sleep(1)
        if channel in ("b","both"):
            print(f"Channel B forward {speed:.0%}")
            drive.set_right_speed(speed)
            time.sleep(duration)
            drive.stop()
            time.sleep(1)
            print(f"Channel B backward {speed:.0%}")
            drive.set_right_speed(-speed)
            time.sleep(duration)
            drive.stop()
        if channel=="both":
            time.sleep(1)
            print(f"Both motors forward {speed:.0%}")
            drive.forward(speed)
            time.sleep(duration)
            drive.stop()
    finally:
        drive.close()
        print("Done")

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--channel",choices=("a","b","both"),default="a")
    parser.add_argument("--speed",type=float,default=0.4)
    parser.add_argument("--duration",type=float,default=1.0)
    args=parser.parse_args()
    if not 0<args.speed<=1:parser.error("--speed must be > 0 and <= 1")
    if args.duration<=0:parser.error("--duration must be > 0")
    run(args.channel,args.speed,args.duration)

if __name__=="__main__":main()
