import asyncio
import json
import subprocess
import tempfile
import wave
from robot.bluetooth.audio_listener import BleAudioListener
from threading import Thread,Lock
from pathlib import Path
from datetime import datetime
from robot.assets.assets import get_assets

from robot.api import actions
from robot.bluetooth.vision.streamer import VisionStreamer
from robot.config import settings
from robot.system.runtime import get_robot
from robot.vision.face_recognition import vision as face_vision
from robot.system.wifi import wifi_manager
from robot.utils.logger import log

ROOT=Path(__file__).resolve().parents[2]
BLE_AUDIO_UUID="6f2d0006-9b7e-4b2a-a1d3-53d9c4e8f210"
class BleAudioReceiver:
    def __init__(self):self.data=bytearray();self.expected=0;self.active=False;self.busy=False
    def write(self,raw):
        if not raw:return
        kind=raw[0]
        if kind==83:
            if self.busy:return
            self.expected=int.from_bytes(raw[1:5],"little") if len(raw)==5 else 0
            self.active=0<self.expected<=24000
            self.data=bytearray()
        elif kind==68 and self.active:
            if len(self.data)+len(raw)-1>self.expected:self.active=False;self.data.clear();return
            self.data.extend(raw[1:])
        elif kind==69 and self.active:
            self.active=False
            if len(self.data)!=self.expected or self.busy:return
            payload=bytes(self.data);self.data.clear();self.busy=True
            Thread(target=self._play,args=(payload,),daemon=True,name="ble-audio").start()
        elif kind==88:self.active=False;self.data.clear()
    def _play(self,payload):
        path=None
        try:
            def decode(value):
                value=(~value)&255;exponent=(value>>4)&7
                sample=((value&15)<<3)+132
                sample=(sample<<exponent)-132
                return -sample if value&128 else sample
            pcm=b"".join(decode(value).to_bytes(2,"little",signed=True) for value in payload)
            with tempfile.NamedTemporaryFile(prefix="spyturtle_ble_",suffix=".wav",delete=False) as temp:path=Path(temp.name)
            with wave.open(str(path),"wb") as wav:wav.setnchannels(1);wav.setsampwidth(2);wav.setframerate(8000);wav.writeframes(pcm)
            robot=get_robot()
            if robot is None or robot.speaker is None:raise RuntimeError("Speaker unavailable")
            if not robot.speaker.play_file(str(path),"ble_message",delete_after=True):raise RuntimeError("Audio playback failed")
            path=None
            log.info(f"[BLE AUDIO] received {len(payload)} bytes")
        except Exception as error:log.error(f"[BLE AUDIO] {error}")
        finally:
            if path:path.unlink(missing_ok=True)
            self.busy=False
_ble_speech_lock=Lock()
_ble_chat_lock=Lock()
_ble_chat_state_lock=Lock()
_ble_chat_state={"id":0,"status":"idle","answer":"","error":""}
def _ble_chat_worker(job_id,text,language):
    try:
        from robot.brain import conversation
        from robot.speech import tts
        result=conversation.ask(text,language)
        answer=result["answer"]
        with _ble_chat_state_lock:_ble_chat_state.update(status="speaking",answer=answer[:180],error="")
        tts.say(answer,language=result["language"])
        with _ble_chat_state_lock:_ble_chat_state.update(status="done")
    except Exception as error:
        log.error(f"[BLE CHAT] {error}")
        with _ble_chat_state_lock:_ble_chat_state.update(status="error",error=str(error)[:150])
    finally:_ble_chat_lock.release()
def _ble_say(text,language):
    try:
        from robot.speech import tts
        tts.say(text,language=language)
    except Exception as error:log.error(f"[BLE SPEECH] {error}")
    finally:_ble_speech_lock.release()

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
    (log.debug if kind=="move" and value=="joystick" else log.info)(f"[BLUETOOTH] command {kind} {value}")
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

_vision_streamer=None
_ble_reset_lock=Lock()
_ble_reset_state={"state":"idle","error":None}
def _ble_reset_worker():
    try:
        from robot.api.admin import reset_turtle,gpio_reset_status
        from starlette.requests import Request
        result=reset_turtle(Request({"type":"http","method":"POST","path":"/admin/turtle/reset","headers":[],"client":("bluetooth",0)}))
        if result.get("state")=="restarting":
            with _ble_reset_lock:_ble_reset_state.update(state="gpio",error=None)
            return
        with _ble_reset_lock:_ble_reset_state.update(state="ready" if result.get("ok") else "failed",error=None if result.get("ok") else str(result)[:120])
    except Exception as error:
        with _ble_reset_lock:_ble_reset_state.update(state="failed",error=str(error)[:120])
def admin_dispatch(request):
    action=str(request.get("action",""))
    data=request.get("data") or {}
    robot=get_robot()
    if action not in ("log_tail","vision_status","ble_vision_status","power_get","volume_get","led_brightness_get","wifi_status","motor_speed_get","motor_correction_get","headlights_color_get","headlights_intensity_get","speech_settings","audio_adaptive_get","turtle_reset_status","chat_status","automation_status","sentinel_status","mood_status","asset_list","photo_list"):log.info(f"[BLUETOOTH ADMIN] {action}")
    elif action!="log_tail":log.debug(f"[BLUETOOTH ADMIN] {action}")
    if action=="log_tail":
        level=str(data.get("level","INFO")).upper()
        if level not in ("DEBUG","INFO","WARN","WARNING","ERROR"):level="INFO"
        # Keep GATT read replies small; the admin characteristic is not a streaming channel.
        count=max(1,min(4,int(data.get("count",4))))
        offset=max(0,min(60,int(data.get("offset",0))))
        history=log.tail(count=count+offset,level=level)
        lines=[line[:110] for line in (history[-(offset+count):-offset] if offset else history[-count:])]
        return {"ok":True,"lines":lines}
    if action=="turtle_reset":
        with _ble_reset_lock:
            if _ble_reset_state["state"]=="restarting":raise RuntimeError("Reset already in progress")
            _ble_reset_state.update(state="restarting",error=None)
        Thread(target=_ble_reset_worker,daemon=True,name="ble-turtle-reset").start()
        return {"ok":True,"state":"restarting"}
    if action=="turtle_reset_status":
        from robot.api.admin import gpio_reset_status
        with _ble_reset_lock:state=dict(_ble_reset_state)
        if state["state"]=="gpio":
            gpio=gpio_reset_status()
            if gpio["state"] in ("ready","failed"):
                with _ble_reset_lock:_ble_reset_state.update(state=gpio["state"],error=gpio.get("error"))
                state=dict(_ble_reset_state)
        return {"ok":True,**state}
    if action=="motor_speed_get":
        if robot is None or robot.motors is None:raise RuntimeError("Motors unavailable")
        return {"ok":True,"speed":robot.motors.get_speed_percent()}
    if action=="motor_speed_set":
        speed=int(data.get("speed",0))
        if not 100<=speed<=300:raise ValueError("Motor speed must be 100..300")
        if robot is None or robot.motors is None:raise RuntimeError("Motors unavailable")
        value=robot.motors.set_speed_percent(speed)
        return {"ok":True,"speed":value,"message":f"Drive speed set to {value}%"}
    if action in ("motor_correction_get","motor_correction_set"):
        if robot is None or robot.motors is None:raise RuntimeError("Motors unavailable")
        motors=robot.motors
        if action=="motor_correction_set":
            state=motors.set_correction_enabled(bool(data.get("enabled")))
        else:state=motors.status().get("encoders",{})
        return {"ok":True,"available":bool(state.get("enabled")),"enabled":bool(state.get("correction_enabled"))}
    if action in ("headlight_color_get","headlight_color_set","headlight_intensity_get","headlight_intensity_set"):
        if robot is None or robot.leds is None:raise RuntimeError("LEDs unavailable")
        leds=robot.leds
        if action=="headlight_color_set":
            import re
            color=str(data.get("color",""))
            if not re.fullmatch(r"#[0-9a-fA-F]{6}",color):raise ValueError("Invalid headlight color")
            return {"ok":True,"color":leds.set_headlights_color(color)}
        if action=="headlight_color_get":return {"ok":True,"color":leds.headlights_color}
        if action=="headlight_intensity_set":
            intensity=int(data.get("intensity",-1))
            if not 0<=intensity<=100:raise ValueError("Headlight intensity must be 0..100")
            return {"ok":True,"intensity":leds.set_headlights_intensity(intensity)}
        return {"ok":True,"intensity":leds.headlights_intensity}
    if action in ("speech_settings","speech_language","speech_voice","speech_tuning"):
        from robot.speech import tts
        if action=="speech_language":tts.set_language(str(data.get("language","")))
        elif action=="speech_voice":tts.set_voice(str(data.get("language","")),str(data.get("voice","")))
        elif action=="speech_tuning":return {"ok":True,**tts.set_tuning(data.get("pitch"),data.get("speed"))}
        return {"ok":True,**{k:v for k,v in tts.status().items() if k in ("language","voice_available","voice","selected_voices","available_voices","pitch","speed")}}
    if action=="audio_adaptive_status":
        if robot is None or robot.speaker is None:raise RuntimeError("Speaker unavailable")
        status=robot.speaker.adaptive_status()
        return {"ok":True,"ambient_rms":status.get("ambient_rms"),"boost":status.get("boost",0),"enabled":status.get("enabled")}
    if action=="chat_status":
        with _ble_chat_state_lock:return {"ok":True,**_ble_chat_state}
    if action=="chat_ask":
        from robot.speech import tts
        message=str(data.get("text","")).strip();language=str(data.get("language") or tts.language())
        if not message or len(message)>250:raise ValueError("Question must contain 1..250 characters")
        if language not in tts.LANGUAGES:raise ValueError("Unsupported language")
        if not _ble_chat_lock.acquire(blocking=False):raise RuntimeError("Conversation already in progress")
        try:
            with _ble_chat_state_lock:
                job_id=_ble_chat_state["id"]+1
                _ble_chat_state.update(id=job_id,status="thinking",answer="",error="")
            Thread(target=_ble_chat_worker,args=(job_id,message,language),daemon=True,name="ble-chat").start()
        except Exception:_ble_chat_lock.release();raise
        return {"ok":True,"id":job_id,"queued":True}
    if action=="speech_say":
        from robot.speech import tts
        message=str(data.get("text","")).strip();language=str(data.get("language") or tts.language())
        if not message or len(message)>250:raise ValueError("Speech text must contain 1..250 characters")
        if language not in tts.LANGUAGES:raise ValueError("Unsupported language")
        if not _ble_speech_lock.acquire(blocking=False):raise RuntimeError("Speech already in progress")
        try:Thread(target=_ble_say,args=(message,language),daemon=True,name="ble-speech").start()
        except Exception:_ble_speech_lock.release();raise
        return {"ok":True,"queued":True}
    if action=="https_add_current_ip":
        result=subprocess.run(["sudo","-n","/usr/local/sbin/spyturtle-add-https-ip"],capture_output=True,text=True,timeout=25)
        if result.returncode:raise RuntimeError((result.stderr or result.stdout or "HTTPS configuration failed").strip()[:150])
        return {"ok":True,"message":result.stdout.strip()[:160]}
    if action=="ble_vision_status":return _vision_streamer.status() if _vision_streamer else {"ok":False,"error":"BLE vision unavailable"}
    if action=="ble_vision_degraded":
        if not _vision_streamer:raise RuntimeError("BLE vision unavailable")
        return _vision_streamer.set_degraded(bool(data.get("enabled")))
    if action=="wifi_authorize_current":
        return {"ok":True,**wifi_manager.authorize_current()}
    if action=="wifi_status":return {"ok":True,**compact_wifi_status()}
    if action=="wifi_add":
        network=wifi_manager.add(str(data.get("nickname","")),str(data.get("ssid","")),str(data.get("password","")))
        return {"ok":True,"message":f"Wi-Fi saved: {network['nickname']}",**network}
    if action=="wifi_connect":
        wifi_manager.connect(str(data.get("ssid","")));return {"ok":True,"message":"Wi-Fi connection requested"}
    if action=="wifi_delete":
        wifi_manager.delete(str(data.get("ssid","")));return {"ok":True,"message":"Wi-Fi network deleted"}
    if robot is None:raise RuntimeError("Robot unavailable")
    if action=="automation_status":return {"ok":True,"enabled":bool(robot.power.data.get("automation_enabled",True)),"sounds":bool(robot.power.data.get("automation_sounds",True))}
    if action=="automation_enable":return {"ok":True,"enabled":bool(robot.power.set_automation(bool(data.get("enabled")))["automation_enabled"])}
    if action=="automation_sounds":return {"ok":True,"sounds":bool(robot.power.set_automation_sounds(bool(data.get("enabled")))["automation_sounds"])}
    if action=="asset_list":
        section=str(data.get("section",""));offset=max(0,int(data.get("offset",0)))
        if section not in ("faces","shell","leds","audio"):raise ValueError("Invalid asset section")
        entries=[{"name":name,"label":str(asset.get("label",name))[:26]} for name,asset in get_assets(section).items()]
        return {"ok":True,"items":entries[offset:offset+3],"total":len(entries)}
    if action=="photo_list":
        offset=max(0,int(data.get("offset",0)))
        folder=ROOT/"photos"
        entries=sorted((p.name for p in folder.iterdir() if p.is_file() and p.suffix.lower() in (".jpg",".jpeg")),reverse=True) if folder.exists() else []
        return {"ok":True,"items":[{"name":n} for n in entries[offset:offset+3]],"total":len(entries)}
    if action=="photo_capture":
        source=str(data.get("source","camera"))
        if source not in ("camera","thermal"):raise ValueError("Invalid photo source")
        content=actions.thermal_frame() if source=="thermal" else actions.camera_frame()
        folder=ROOT/"photos";folder.mkdir(exist_ok=True)
        name=("thermal_" if source=="thermal" else "")+datetime.now().strftime("%Y%m%d_%H%M%S_%f")+".jpg"
        (folder/name).write_bytes(content)
        return {"ok":True,"name":name,"source":source}
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
    global _vision_streamer
    from bless import BlessGATTCharacteristic,BlessServer,GATTAttributePermissions,GATTCharacteristicProperties
    loop=asyncio.get_running_loop()
    server=BlessServer(name=settings.BLUETOOTH_NAME,loop=loop)
    admin_response=bytearray(b'{"ok":true}')
    vision=None
    audio=BleAudioReceiver()
    listener=BleAudioListener(server,settings.BLUETOOTH_SERVICE_UUID,BLE_AUDIO_UUID)

    def characteristic_uuid(characteristic): return str(getattr(characteristic,"uuid","")).lower()

    def read_request(characteristic:BlessGATTCharacteristic,**kwargs):
        if characteristic_uuid(characteristic) in (settings.BLUETOOTH_CAMERA_UUID.lower(),BLE_AUDIO_UUID):return bytearray()
        if characteristic_uuid(characteristic)==settings.BLUETOOTH_ADMIN_UUID.lower():return admin_response
        return bytearray(json.dumps(compact_state(),separators=(",",":")).encode())

    def write_request(characteristic:BlessGATTCharacteristic,value,**kwargs):
        nonlocal admin_response
        try:
            raw=bytes(value)
            if characteristic_uuid(characteristic)==BLE_AUDIO_UUID:
                if raw in (b"L",b"Q"):listener.request(raw)
                else:audio.write(raw)
                return
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
    await server.add_new_characteristic(settings.BLUETOOTH_SERVICE_UUID,BLE_AUDIO_UUID,GATTCharacteristicProperties.write|GATTCharacteristicProperties.notify,bytearray(),GATTAttributePermissions.writeable)
    vision=VisionStreamer(server,settings.BLUETOOTH_SERVICE_UUID,settings.BLUETOOTH_CAMERA_UUID,
        chunk=settings.BLUETOOTH_VISION_CHUNK,interval=settings.BLUETOOTH_VISION_INTERVAL) if settings.BLUETOOTH_VISION_ENABLED else None
    _vision_streamer=vision
    await server.start()
    log.info(f"[BLUETOOTH] ready name={settings.BLUETOOTH_NAME}")
    try:
        while True:await asyncio.sleep(3600)
    finally:
        listener.stop()
        await server.stop()

def run_bluetooth():
    try:asyncio.run(serve())
    except ImportError:log.warn("[BLUETOOTH] bless is not installed; run scripts/install/configure_bluetooth.sh")
    except Exception as error:log.warn(f"[BLUETOOTH] unavailable: {error}")
