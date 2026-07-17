from luma.core.interface.serial import i2c
from luma.oled.device import ssd1306
from PIL import Image, ImageDraw, ImageFont
import time


serial = i2c(port=1, address=0x3C)

device = ssd1306(serial)

image = Image.new("1", (128, 64))
draw = ImageDraw.Draw(image)

font = ImageFont.load_default()

draw.text(
    (0, 0),
    "Spy Turtle",
    font=font,
    fill=255
)

draw.text(
    (0, 20),
    "OLED TEST OK",
    font=font,
    fill=255
)

device.display(image)

time.sleep(10)
