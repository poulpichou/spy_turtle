import time
import threading

from robot.factory.robot_factory import RobotFactory
from robot.system.runtime import set_robot
from robot.config import settings
from robot.utils.logger import log


def start_api():
    import uvicorn
    from robot.api.app import app

    log.info("Starting API")
    uvicorn.run(app,host=settings.API_HOST,port=settings.API_PORT)


def main():
    log.info("Starting Spy Turtle")

    robot=RobotFactory(simulation=settings.SIMULATION).create()
    set_robot(robot)

    log.info("Robot ready")

    threading.Thread(target=start_api,daemon=True).start()

    delay=1/settings.UPDATE_RATE

    log.info("Main loop started")

    while True:
        robot.update()
        time.sleep(delay)


if __name__=="__main__":
    main()