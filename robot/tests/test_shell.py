from robot.hardware.shell_screen_st7796 import ShellScreenST7796
import time

screen=ShellScreenST7796()

screen.text("TEST",[
    "SPI OK",
    "ST7796",
    "Spy Turtle"
])

time.sleep(10)