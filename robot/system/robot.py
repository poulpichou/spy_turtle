import time
from threading import Thread,Lock,Event
from robot.vision.face_recognition import vision as face_vision
from robot.system.state import TurtleState
from robot.system.power import PowerManager
from robot.brain.sentinel import Sentinel

class Robot:
    BATTERY_UPDATE_INTERVAL=2.0
    IDLE_BATTERY_UPDATE_INTERVAL=30.0

    def __init__(self,motors,face,leds,camera,battery,speaker,servo,shell=None,thermal_camera=None,distance_sensor=None,environment_sensor=None):
        self.motors=motors
        self.face=face
        self.leds=leds
        self.camera=camera
        self.thermal_camera=thermal_camera
        self.distance_sensor=distance_sensor
        self.environment_sensor=environment_sensor
        self.battery=battery
        self.speaker=speaker
        self.servo=servo
        self.shell=shell
        self.state=TurtleState()
        self.brain=None
        self._actuator_reset_lock=Lock()
        self._actuator_reset_request=None
        self._last_battery_update=0.0
        self._last_background_vision=0.0
        self._last_ambient_sample=0.0
        self._ambient_sample_running=False
        self._background_vision_running=False
        self.power=PowerManager(self)
        self.sentinel=Sentinel()
        self._update_battery(force=True)
        if self.face:self.face.play('neutral')
        from robot.utils.logger import log
        log.info("[ROBOT] initialized")

    def request_actuator_reset(self,timeout=20):
        with self._actuator_reset_lock:
            if self._actuator_reset_request is not None:raise RuntimeError('Actuator reset already in progress')
            request={'event':Event(),'result':None};self._actuator_reset_request=request
        if not request['event'].wait(timeout):raise TimeoutError('Actuator reset timed out; check robot logs')
        return dict(request['result'])

    def _process_actuator_reset(self):
        with self._actuator_reset_lock:request=self._actuator_reset_request
        if request is None:return
        from robot.api.actions import disarm_motion
        from robot.hardware.motor import DifferentialDrive
        from robot.hardware.servo import ServoController
        from robot.config import settings
        from robot.utils.logger import log
        result={'motors':'not attempted','servos':'not attempted'}
        try:
            disarm_motion();self.state.motion='stop'
            old_motors=self.motors;old_servo=self.servo
            self.motors=None;self.servo=None
            if old_motors:
                try:old_motors.close();result['motors_close']='ok'
                except Exception as error:result['motors_close']=str(error);log.error(f'[RESET] motors close: {error}')
            if old_servo:
                try:old_servo.close();result['servos_close']='ok'
                except Exception as error:result['servos_close']=str(error);log.error(f'[RESET] servos close: {error}')
            if settings.SIMULATION:
                from robot.simulation.fake_motor import FakeMotor
                from robot.simulation.fake_servo import FakeServo
                self.motors=FakeMotor();self.servo=FakeServo()
            else:
                try:self.motors=DifferentialDrive();result['motors']='ok'
                except Exception as error:result['motors']=f'ERROR: {error}';log.error(f'[RESET] motors create: {error}')
                try:self.servo=ServoController();result['servos']='ok'
                except Exception as error:result['servos']=f'ERROR: {error}';log.error(f'[RESET] servos create: {error}')
            if settings.SIMULATION:result.update(motors='ok',servos='ok')
            result['ok']=result['motors']=='ok' and result['servos']=='ok' and all(result.get(k)=='ok' for k in ('motors_close','servos_close') if k in result)
            log.info(f'[RESET] actuator reconstruction completed: {result}')
        except Exception as error:
            result['ok']=False;result['error']=str(error);log.error(f'[RESET] actuator reconstruction failed: {error}')
        finally:
            with self._actuator_reset_lock:
                request['result']=result
                self._actuator_reset_request=None
                request['event'].set()

    def update(self):
        self._process_actuator_reset()
        from robot.api.actions import motion_watchdog
        motion_watchdog()
        if self.motors and hasattr(self.motors,'update'):self.motors.update()
        if self.power.idle_mode:
            self._update_battery(interval=self.IDLE_BATTERY_UPDATE_INTERVAL)
            if self.shell and hasattr(self.shell,'update_touch_only'):self.shell.update_touch_only()
            return
        self._update_battery()
        self._update_background_vision()
        self._update_ambient_audio()
        self.state.vision=face_vision.observations()
        self.sentinel.update(self)
        if self.brain:self.brain.update()
        if self.servo:self.servo.update()
        if self.leds:self.leds.update()
        if self.face and self.face.update():
            self.state.face_event_until=0.0
        if self.shell:
            self.shell.update()
            if hasattr(self.shell.screen,'update'):self.shell.screen.update()

    def _update_ambient_audio(self):
        if not self.speaker or not getattr(self.speaker,"adaptive_enabled",False) or not self.power.data.get("automation_enabled",True) or self.power.idle_mode:return
        now=time.monotonic()
        if self._ambient_sample_running or now-self._last_ambient_sample<30:return
        self._last_ambient_sample=now;self._ambient_sample_running=True
        def measure():
            try:self.speaker.sample_ambient()
            finally:self._ambient_sample_running=False
        Thread(target=measure,daemon=True,name="ambient-audio").start()

    def _update_background_vision(self):
        if not self.power.data.get("automation_enabled",True) or not self.sentinel.config.get("enabled",False) or not face_vision.enabled or not self.camera:return
        now=time.monotonic()
        if self._background_vision_running or now-self._last_background_vision<5.0:return
        self._last_background_vision=now;self._background_vision_running=True
        def capture():
            try:face_vision.submit(self.camera.get_frame())
            except Exception as error:
                from robot.utils.logger import log
                log.warn(f"[FACE BACKGROUND] {error}")
            finally:self._background_vision_running=False
        Thread(target=capture,daemon=True,name="face-background-capture").start()

    @staticmethod
    def _battery_status(level,charging):
        if charging:return 'charging'
        if level is None:return 'unknown'
        if level<=5:return 'critical'
        if level<=20:return 'low'
        if level<=50:return 'medium'
        if level<95:return 'high'
        return 'full'

    def _update_battery(self,force=False,interval=None):
        now=time.monotonic()
        interval=self.BATTERY_UPDATE_INTERVAL if interval is None else interval
        if not force and now-self._last_battery_update<interval:return
        self._last_battery_update=now
        if not self.battery:
            self.state.battery={**self.state.battery,'error':'Battery component unavailable','updated_at':None}
            return
        from robot.utils.logger import log
        stage='level'
        try:
            level=float(self.battery.get_level());log.debug(f'[BATTERY] level={level:.1f}%')
            stage='voltage';voltage=float(self.battery.get_voltage());log.debug(f'[BATTERY] voltage={voltage:.3f}V')
            stage='current';current=float(self.battery.get_current());log.debug(f'[BATTERY] current={current:.3f}mA')
            stage='charging';charging=bool(self.battery.is_charging());log.debug(f'[BATTERY] charging={charging}')
            stage='cells';cells=list(self.battery.get_cells());log.debug(f'[BATTERY] cells_mv={cells}')
            stage='remaining_capacity';remaining=self.battery.get_remaining_capacity();log.debug(f'[BATTERY] remaining_capacity={remaining}')
            stage='usb_connected';usb=bool(self.battery.usb_connected());log.debug(f'[BATTERY] usb_connected={usb}')
            self.state.battery={
                'level':round(level,1),'status':self._battery_status(level,charging),'voltage_v':round(voltage,3),
                'current_a':round(current,3),'power_w':round(voltage*current,3),'cells_mv':cells,
                'remaining_capacity':remaining,'charging':charging,
                'usb_connected':usb,'updated_at':time.time(),'error':None
            }
        except Exception as error:
            log.error(f"[BATTERY] {stage} read failed: {type(error).__name__}: {error}")
            self.state.battery={'level':None,'status':'unknown','voltage_v':None,'current_a':None,'power_w':None,'cells_mv':[],'remaining_capacity':None,'charging':None,'usb_connected':None,'updated_at':None,'error':str(error)}
            log.debug(f"[BATTERY] update aborted at stage={stage}")

    def forward(self): self.motors.forward()
    def backward(self): self.motors.backward()
    def turn_left(self): self.motors.left()
    def turn_right(self): self.motors.right()
    def stop(self): self.motors.stop()

    def set_emotion(self,emotion):
        if self.brain and hasattr(self.brain,'moods'):
            try:self.brain.moods.choose(emotion);return
            except ValueError:pass
        self.state.emotion=emotion
        if self.face:self.face.play(emotion)

    def shell_mode(self,mode):
        if self.shell:self.shell.set_mode(mode)

    def shell_event(self,event):
        if self.shell:self.shell.trigger(event)
