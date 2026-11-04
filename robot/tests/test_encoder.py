from gpiozero import DigitalInputDevice
from time import sleep, monotonic

LEFT_PIN = 14
RIGHT_PIN = 15

counts = {"left": 0, "right": 0}

def count_left():
    counts["left"] += 1

def count_right():
    counts["right"] += 1

def main():
    left = DigitalInputDevice(LEFT_PIN, pull_up=True)
    right = DigitalInputDevice(RIGHT_PIN, pull_up=True)
    left.when_activated = count_left
    right.when_activated = count_right
    print("[Encoder] Ready - rotate wheels by hand (Ctrl+C to stop)")
    try:
        while True:
            print(f"Left: {counts['left']:6d} | Right: {counts['right']:6d}")
            sleep(0.5)
    except KeyboardInterrupt:
        print("\n[Encoder] Stopped")
    finally:
        left.close()
        right.close()

if __name__ == "__main__":
    main()

