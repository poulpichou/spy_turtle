from robot.hardware.camera import Camera
import time

camera=Camera()

camera.start()
time.sleep(2)

camera.capture("camera_test.jpg")

camera.stop()

print("Done")