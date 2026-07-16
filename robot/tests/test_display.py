import time

from robot.hardware.display.display import Display


screen = Display()

try:

    screen.start()

    screen.clear()

    screen.text(
        50,
        50,
        "SPY TURTLE"
    )

    screen.rectangle(
        40,
        120,
        200,
        80,
        screen.GREEN
    )

    screen.show()

    time.sleep(10)

finally:

    screen.close()
