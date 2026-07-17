import time
import threading
import uvicorn

from robot.factory.robot_factory import RobotFactory
from robot.system.runtime import set_robot
from robot.api.app import app

def start_api():
    uvicorn.run(app, host="0.0.0.0", port=8000)

def main():
    print("[Startup] Starting Spy Turtle")
    robot=RobotFactory(simulation=False).create()
    set_robot(robot)
    print("Spy Turtle online")

    api_thread = threading.Thread(target=start_api, daemon=True)
    api_thread.start()
    print("[Startup] API started")

    while True:
        robot.update()
        time.sleep(0.5)

if __name__ == "__main__":
    main()