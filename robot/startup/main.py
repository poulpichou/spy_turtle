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
    uvicorn.run(app,host=settings.API_HOST,port=settings.API_PORT,access_log=False)

def start_bluetooth():
    try:
        from robot.bluetooth.server import run_bluetooth
        run_bluetooth()
    except Exception as error:log.warn(f"[BLUETOOTH] disabled after startup error: {error}")

def main():
    log.info("Starting Spy Turtle")
    robot=RobotFactory(simulation=settings.SIMULATION).create()
    set_robot(robot)
    # Default ON at startup; Admin can disable recognition for this session.
    if not settings.SIMULATION:
        try:
            from robot.vision.face_recognition import vision
            vision.enable(True)
        except Exception as exc:log.warn(f"[FACE] Auto-enable failed: {exc}")
    health=HealthMonitor(robot)
    log.info("Robot ready")
    threading.Thread(target=start_api,daemon=True).start()
    if settings.BLUETOOTH_ENABLED and not settings.SIMULATION:threading.Thread(target=start_bluetooth,daemon=True).start()
    delay=1/settings.UPDATE_RATE
    log.info("Main loop started")
    from robot.system.actuator_diagnostics import tick,record
    while True:
        try:
            robot.update()
            health.update()
        except Exception as error:
            record("LOOP",f"EXCEPTION {type(error).__name__}: {error}")
            raise
        finally:tick()
        time.sleep(delay)

if __name__=="__main__":main()
