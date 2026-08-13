import asyncio
import json
import subprocess
from pathlib import Path

from robot.api import actions
from robot.config import settings
from robot.system.runtime import get_robot
from robot.system.wifi import wifi_manager
from robot.utils.logger import log

ROOT=Path(__file__).resolve().parents[2]

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

def compact_wifi_status():
    status=wifi_manager.status()
    networks=[{"ssid":item["ssid"],"nickname":item["nickname"],"active":item["active"]} for item in status.get("networks",[])][:5]
    current=status.get("current")
    current={"ssid":current["ssid"],"nickname":current["nickname"],"active":True} if current else None
    return {"networks":networks,"current":current}

def detached(command): subprocess.Popen(command,cwd=ROOT,start_new_session=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)

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

def admin_dispatch(request):
    action=str(request.get("action",""))
    data=request.get("data") or {}
    robot=get_robot()
    log.info(f"[BLUETOOTH ADMIN] {action}")
    if action=="wifi_status":return {"ok":True,**compact_wifi_status()}
    if action=="wifi_add":
        network=wifi_manager.add(str(data.get("nickname","")),str(data.get("ssid","")),str(data.get("password","")))
        return {"ok":True,"message":f"Wi-Fi saved: {network['nickname']}",**network}
    if action=="wifi_connect":
        wifi_manager.connect(str(data.get("ssid","")));return {"ok":True,"message":"Wi-Fi connection requested"}
    if action=="wifi_delete":
        wifi_manager.delete(str(data.get("ssid","")));return {"ok":True,"message":"Wi-Fi network deleted"}
    if robot is None:raise RuntimeError("Robot unavailable")
    if action=="volume_get":
        if robot.speaker is None:raise RuntimeError("Speaker unavailable")
        return {"ok":True,**robot.speaker.status()}
    if action=="volume_set":
        if robot.speaker is None:raise RuntimeError("Speaker unavailable")
        robot.speaker.set_volume(int(data.get("volume",60)))
        return {"ok":True,"volume":robot.speaker.volume,"message":f"Volume set to {robot.speaker.volume}%"}
    if action=="power_get":return {"ok":True,**robot.power.status()}
    if action=="power_component":return {"ok":True,**robot.power.set_component(str(data.get("component","")),bool(data.get("enabled")))}
    if action=="idle":return {"ok":True,**robot.power.set_idle(bool(data.get("enabled")))}
    if action=="microphone_sensitivity":return {"ok":True,**robot.power.set_microphone_sensitivity(int(data.get("sensitivity",60)))}
    if action=="restart":
        detached(["bash","-lc","sleep 1; ./scripts/stop_turtle.sh; sleep 1; ./scripts/start_turtle.sh"])
        return {"ok":True,"message":"Spy Turtle restart requested"}
    if action=="reboot":
        detached(["sudo","-n","reboot"]);return {"ok":True,"message":"Reboot requested"}
    if action=="shutdown":
        detached(["sudo","-n","shutdown","now"]);return {"ok":True,"message":"Shutdown requested"}
    raise ValueError(f"Unknown admin action: {action}")

async def serve():
    from bless import BlessGATTCharacteristic,BlessServer,GATTAttributePermissions,GATTCharacteristicProperties
    loop=asyncio.get_running_loop()
    server=BlessServer(name=settings.BLUETOOTH_NAME,loop=loop)
    admin_response=bytearray(b'{"ok":true}')

    def characteristic_uuid(characteristic): return str(getattr(characteristic,"uuid","")).lower()

    def read_request(characteristic:BlessGATTCharacteristic,**kwargs):
        if characteristic_uuid(characteristic)==settings.BLUETOOTH_ADMIN_UUID.lower():return admin_response
        return bytearray(json.dumps(compact_state(),separators=(",",":")).encode())

    def write_request(characteristic:BlessGATTCharacteristic,value,**kwargs):
        nonlocal admin_response
        try:
            payload=json.loads(bytes(value).decode("utf-8"))
            if characteristic_uuid(characteristic)==settings.BLUETOOTH_ADMIN_UUID.lower():
                try:result=admin_dispatch(payload)
                except Exception as error:
                    log.error(f"[BLUETOOTH ADMIN ERROR] {error}")
                    result={"ok":False,"error":str(error)}
                admin_response=bytearray(json.dumps(result,separators=(",",":")).encode())
            else:dispatch(payload)
        except Exception as error:log.error(f"[BLUETOOTH ERROR] {error}")

    server.read_request_func=read_request
    server.write_request_func=write_request
    await server.add_new_service(settings.BLUETOOTH_SERVICE_UUID)
    await server.add_new_characteristic(
        settings.BLUETOOTH_SERVICE_UUID,settings.BLUETOOTH_COMMAND_UUID,
        GATTCharacteristicProperties.write|GATTCharacteristicProperties.write_without_response,
        None,GATTAttributePermissions.writeable
    )
    await server.add_new_characteristic(
        settings.BLUETOOTH_SERVICE_UUID,settings.BLUETOOTH_STATE_UUID,
        GATTCharacteristicProperties.read,
        bytearray(b"{}"),GATTAttributePermissions.readable
    )
    await server.add_new_characteristic(
        settings.BLUETOOTH_SERVICE_UUID,settings.BLUETOOTH_ADMIN_UUID,
        GATTCharacteristicProperties.read|GATTCharacteristicProperties.write,
        bytearray(b'{"ok":true}'),GATTAttributePermissions.readable|GATTAttributePermissions.writeable
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
