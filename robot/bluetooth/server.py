import asyncio
import json

from robot.api import actions
from robot.config import settings
from robot.system.runtime import get_robot
from robot.utils.logger import log

def compact_state():
    robot=get_robot()
    if robot is None:return {"error":"no robot"}
    data=robot.state.to_dict()
    battery=data.get("battery",{})
    return {
        "battery":{"level":battery.get("level"),"status":battery.get("status")},
        "brain":{"emotion":data.get("brain",{}).get("emotion","neutral")},
        "shell":{"mode":data.get("shell",{}).get("mode","status")},
        "leds":{"mode":data.get("leds",{}).get("mode","off")},
        "motion":{"state":data.get("motion",{}).get("state","stop")}
    }

def dispatch(command):
    kind=str(command.get("type",""))
    value=str(command.get("value",""))
    extra=command.get("extra") or {}
    log.info(f"[BLUETOOTH] command {kind} {value}")
    if kind=="move":
        speed=extra.get("speed")
        if speed is not None:speed=float(speed)
        if value=="forward":actions.move_forward(speed)
        elif value=="backward":actions.move_backward(speed)
        elif value=="left":actions.turn_left(speed)
        elif value=="right":actions.turn_right(speed)
        elif value=="stop":actions.stop()
        else:raise ValueError(f"Unknown movement: {value}")
    elif kind=="face":actions.set_emotion(value)
    elif kind=="led":actions.set_led(value)
    elif kind=="shell":actions.shell_show(value)
    elif kind=="shell_text":actions.shell_text(value)
    elif kind=="head":
        if value=="left":actions.look_left()
        elif value=="right":actions.look_right()
        elif value=="up":actions.look_up()
        elif value=="down":actions.look_down()
        elif value=="center":actions.camera_center()
        else:raise ValueError(f"Unknown head command: {value}")
    elif kind=="sound":actions.speak(value)
    else:raise ValueError(f"Unknown command type: {kind}")

async def serve():
    from bless import BlessGATTCharacteristic,BlessServer,GATTAttributePermissions,GATTCharacteristicProperties
    loop=asyncio.get_running_loop()
    server=BlessServer(name=settings.BLUETOOTH_NAME,loop=loop)

    def read_request(characteristic:BlessGATTCharacteristic,**kwargs):
        return bytearray(json.dumps(compact_state(),separators=(",",":")).encode())

    def write_request(characteristic:BlessGATTCharacteristic,value,**kwargs):
        try:dispatch(json.loads(bytes(value).decode("utf-8")))
        except Exception as error:log.error(f"[BLUETOOTH ERROR] {error}")

    server.read_request_func=read_request
    server.write_request_func=write_request
    await server.add_new_service(settings.BLUETOOTH_SERVICE_UUID)
    await server.add_new_characteristic(
        settings.BLUETOOTH_SERVICE_UUID,settings.BLUETOOTH_COMMAND_UUID,
        GATTCharacteristicProperties.write|GATTCharacteristicProperties.write_without_response,
        None,GATTAttributePermissions.writable
    )
    await server.add_new_characteristic(
        settings.BLUETOOTH_SERVICE_UUID,settings.BLUETOOTH_STATE_UUID,
        GATTCharacteristicProperties.read,
        bytearray(b"{}"),GATTAttributePermissions.readable
    )
    await server.start()
    log.info(f"[BLUETOOTH] ready name={settings.BLUETOOTH_NAME}")
    try:
        while True:await asyncio.sleep(3600)
    finally:await server.stop()

def run_bluetooth():
    try:asyncio.run(serve())
    except ImportError:log.warn("[BLUETOOTH] bless is not installed; run scripts/configure_bluetooth.sh")
    except Exception as error:log.warn(f"[BLUETOOTH] unavailable: {error}")
