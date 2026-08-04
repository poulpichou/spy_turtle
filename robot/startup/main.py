import threading
import time

from robot.api.app import app
from robot.config import settings
from robot.factory.robot_factory import RobotFactory
from robot.system.health_monitor import HealthMonitor
from robot.system.runtime import set_robot
from robot.utils.logger import log

def start_api():
    import uvicorn
    log.info("Starting API")
    uvicorn.run(app,host=settings.API_HOST,port=settings.API_PORT)

def main():
    log.info("Starting Spy Turtle")
    robot=RobotFactory(simulation=settings.SIMULATION).create()
    set_robot(robot)

    # TEMPORARY HARDWARE TEST: keep all 32 LEDs solid red.
    robot.leds.set_mode("red")
    robot.state.led_mode="red"
    log.info("[LED TEST] 32 LEDs set to solid red")

    health=HealthMonitor(robot)
    log.info("Robot ready")
    threading.Thread(target=start_api,daemon=True).start()
    delay=1/settings.UPDATE_RATE
    log.info("Main loop started")
    while True:
        robot.update()
        health.update()
        time.sleep(delay)

if __name__=="__main__":
    main()