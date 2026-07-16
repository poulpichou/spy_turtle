import time

from robot.hardware.display.st7796 import ST7796


screen = ST7796()

try:
    screen.init()

    print("Fill RED")

    # RGB565 rouge
    screen.fill(0xF800)

    time.sleep(10)

finally:
    screen.close()
