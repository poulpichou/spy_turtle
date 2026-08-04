import os
import subprocess
import time

from robot.config import settings
from robot.utils.logger import log

class HealthMonitor:
    def __init__(self,robot):
        self.robot=robot
        self.started_at=time.monotonic()
        self.last_heartbeat=0.0
        self.last_health=0.0

    def update(self):
        now=time.monotonic()
        if now-self.last_heartbeat>=settings.HEARTBEAT_INTERVAL:
            self.last_heartbeat=now
            log.info(f"[HEARTBEAT] alive uptime={self._duration(now-self.started_at)}")
        if now-self.last_health>=settings.HEALTH_INTERVAL:
            self.last_health=now
            self._log_health()

    def _log_health(self):
        battery=self.robot.state.battery or {}
        level=self._value(battery.get("level"),"%")
        voltage=self._value(battery.get("voltage_v"),"V")
        current=self._value(battery.get("current_a"),"A")
        power=self._value(battery.get("power_w"),"W")
        cells=",".join(str(value) for value in battery.get("cells_mv",[])) or "--"
        charging=self._bool(battery.get("charging"))
        usb=self._bool(battery.get("usb_connected"))
        temp=self._temperature()
        memory=self._memory()
        load=self._load()
        throttled=self._throttled()
        log.info(
            f"[HEALTH] battery={level} voltage={voltage} current={current} power={power} "
            f"cells_mv={cells} charging={charging} usb={usb} temp={temp} "
            f"memory={memory} load={load} throttled={throttled}"
        )

    @staticmethod
    def _temperature():
        try:
            with open("/sys/class/thermal/thermal_zone0/temp",encoding="utf-8") as file:
                return f"{int(file.read().strip())/1000:.1f}C"
        except (OSError,ValueError): return "--"

    @staticmethod
    def _memory():
        try:
            values={}
            with open("/proc/meminfo",encoding="utf-8") as file:
                for line in file:
                    key,value,*_=line.replace(":","").split()
                    if key in ("MemTotal","MemAvailable"): values[key]=int(value)
            used=values["MemTotal"]-values["MemAvailable"]
            return f"{used/values['MemTotal']*100:.1f}%"
        except (OSError,KeyError,ValueError,ZeroDivisionError): return "--"

    @staticmethod
    def _load():
        try: return f"{os.getloadavg()[0]:.2f}"
        except OSError: return "--"

    @staticmethod
    def _throttled():
        try:
            result=subprocess.run(
                ["vcgencmd","get_throttled"],
                capture_output=True,text=True,timeout=2,check=False
            )
            return result.stdout.strip().removeprefix("throttled=") or "--"
        except (OSError,subprocess.TimeoutExpired): return "--"

    @staticmethod
    def _duration(seconds):
        seconds=int(seconds)
        hours,remainder=divmod(seconds,3600)
        minutes,seconds=divmod(remainder,60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    @staticmethod
    def _value(value,suffix):
        if value is None:return "--"
        return f"{value}{suffix}"

    @staticmethod
    def _bool(value):
        if value is None:return "--"
        return "yes" if value else "no"