import asyncio
import json
import subprocess
from pathlib import Path

from robot.api import actions
from robot.bluetooth.vision.streamer import VisionStreamer
from robot.config import settings
from robot.system.runtime import get_robot
from robot.vision.face_recognition import vision as face_vision
from robot.system.wifi import wifi_manager
from robot.utils.logger import log

ROOT=Path(__file__).resolve().parents[2]

def compact_state():
    robot=get_robot()
    if robot is None:return {"error":"no robot"}
    data=robot.state.to_dict()
    def safe_status(component):
        if component is None:return {}
        try:return component.status()
        except Exception as error:return {"available":False,"error":str(error)}
    env=safe_status(robot.environment_sensor)
    dist=safe_status(robot.distance_sensor)
    servo=safe_status(robot.servo)
    # Only the fields used by the dashboard; preserve REST field names.
    return {
        "battery":{"level":data["battery"].get("level"),"status":data["battery"].get("status"),"charging":data["battery"].get("charging")},
        "brain":{"emotion":data["brain"].get("emotion","neutral"),"mood":data["brain"].get("mood")},
        "shell":{"mode":data["shell"].get("mode","status")},
        "leds":{"mode":data["leds"].get("mode","off")},
        "motion":{"state":data["motion"].get("state","stop")},
        "servo":{"pan":{"current":(servo.get("pan") or {}).get("current")},"tilt":{"current":(servo.get("tilt") or {}).get("current")}},
        "sensors":{"environment":{k:env.get(k) for k in ("temperature_c","humidity_percent","pressure_hpa","pressure_atm","gas_ohms","air_quality")},"distance":{k:dist.get(k) for k in ("distance_mm","out_of_range")}}
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
        if value=="joystick":actions.move_joystick(extra["left"],extra["right"])
        elif value=="forward":actions.move_forward(speed)
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
    if action=="mood_status":
        return {"ok":True,**{k:v for k,v in robot.brain.moods.status().items() if k!="variants"}}
    if action=="mood_list":
        entries=robot.brain.moods.status()["variants"];offset=max(0,int(data.get("offset",0)))
        return {"ok":True,"variants":entries[offset:offset+5],"total":len(entries)}
    if action=="mood_select":
        return {"ok":True,**{k:v for k,v in robot.brain.moods.choose(str(data.get("variant",""))).items() if k!="variants"}}
    if action=="head_movements":
        return {"ok":True,**{k:v for k,v in robot.brain.moods.set_head_enabled(bool(data.get("enabled"))).items() if k!="variants"}}
    if action=="headlights":
        return {"ok":True,**{k:v for k,v in robot.brain.moods.set_headlights(bool(data.get("enabled"))).items() if k!="variants"}}
    if action=="sentinel_status":return {"ok":True,"enabled":bool(robot.sentinel.status().get("enabled",False))}
    if action=="sentinel_enable":return {"ok":True,"enabled":bool(robot.sentinel.set_enabled(bool(data.get("enabled"))).get("enabled",False))}
    if action=="vision_status":
        status=face_vision.status()
        return {"ok":True,"enabled":status["enabled"],"interval":status["interval"],"faces":[{k:round(f[k],3) if k!="name" else str(f[k])[:24] for k in ("x","y","w","h","name")} for f in status["faces"][:4]],"references":status["references"],"errors":status["errors"],"last_ms":status.get("last_ms")}
    if action=="vision_enable":return {"ok":True,**{k:v for k,v in face_vision.enable(bool(data.get("enabled"))).items() if k in ("enabled","interval","references","errors")}}
    if action=="vision_interval":return {"ok":True,**{k:v for k,v in face_vision.configure(int(data.get("interval",2))).items() if k in ("enabled","interval","references","errors")}}
    if action=="led_brightness_get":
        if robot.leds is None:raise RuntimeError("LEDs unavailable")
        return {"ok":True,"brightness":robot.leds.get_brightness_percent()}
    if action=="led_brightness_set":
        if robot.leds is None:raise RuntimeError("LEDs unavailable")
        return {"ok":True,"brightness":robot.leds.set_brightness_percent(int(data.get("brightness",100)))}
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
    vision=None

    def characteristic_uuid(characteristic): return str(getattr(characteristic,"uuid","")).lower()

    def read_request(characteristic:BlessGATTCharacteristic,**kwargs):
        if characteristic_uuid(characteristic)==settings.BLUETOOTH_CAMERA_UUID.lower():return bytearray()
        if characteristic_uuid(characteristic)==settings.BLUETOOTH_ADMIN_UUID.lower():return admin_response
        return bytearray(json.dumps(compact_state(),separators=(",",":")).encode())

    def write_request(characteristic:BlessGATTCharacteristic,value,**kwargs):
        nonlocal admin_response
        try:
            raw=bytes(value)
            if characteristic_uuid(characteristic)==settings.BLUETOOTH_CAMERA_UUID.lower():
                if vision is not None:vision.request(raw)
                return
            payload=json.loads(raw.decode("utf-8"))
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
    await server.add_new_characteristic(
        settings.BLUETOOTH_SERVICE_UUID,settings.BLUETOOTH_CAMERA_UUID,
        GATTCharacteristicProperties.notify|GATTCharacteristicProperties.write,
        bytearray(b""),GATTAttributePermissions.writeable
    )
    vision=VisionStreamer(server,settings.BLUETOOTH_SERVICE_UUID,settings.BLUETOOTH_CAMERA_UUID,
        chunk=settings.BLUETOOTH_VISION_CHUNK,interval=settings.BLUETOOTH_VISION_INTERVAL) if settings.BLUETOOTH_VISION_ENABLED else None
    await server.start()
    log.info(f"[BLUETOOTH] ready name={settings.BLUETOOTH_NAME}")
    try:
        while True:await asyncio.sleep(3600)
    finally:await server.stop()

def run_bluetooth():
    try:asyncio.run(serve())
    except ImportError:log.warn("[BLUETOOTH] bless is not installed; run scripts/configure_bluetooth.sh")
    except Exception as error:log.warn(f"[BLUETOOTH] unavailable: {error}")
