import time
from robot.config import settings
from robot.utils.logger import log

class DistanceSensor:
    def __init__(self):
        import board
        self.i2c=board.I2C();self.address=settings.DISTANCE_SENSOR_ADDRESS;self.minimum_interval=settings.DISTANCE_SENSOR_UPDATE_INTERVAL
        self.last_read_monotonic=0.0;self.last_updated_at=None;self.last_distance_mm=None;self.last_error=None;self.model=None;self.sensor=None;self._read_value=None
        self._init_sensor();log.info(f"[DISTANCE] {self.model} ready address=0x{self.address:02X}")
    def _init_sensor(self):
        errors=[]
        try:
            import adafruit_vl53l1x
            self.sensor=adafruit_vl53l1x.VL53L1X(self.i2c,address=self.address);self.sensor.start_ranging();self.model="VL53L1X";self._read_value=self._read_vl53l1x;return
        except Exception as error:errors.append(f"VL53L1X: {error}")
        try:
            import adafruit_vl53l0x
            self.sensor=adafruit_vl53l0x.VL53L0X(self.i2c,address=self.address);self.model="VL53L0X";self._read_value=self._read_vl53l0x;return
        except Exception as error:errors.append(f"VL53L0X: {error}")
        raise RuntimeError("Unable to detect VL53L0X/VL53L1X: "+"; ".join(errors))
    def _read_vl53l0x(self):return int(self.sensor.range)
    def _read_vl53l1x(self):
        if hasattr(self.sensor,"data_ready") and not self.sensor.data_ready:return self.last_distance_mm
        value=self.sensor.distance
        if hasattr(self.sensor,"clear_interrupt"):self.sensor.clear_interrupt()
        return None if value is None else int(round(float(value)*10.0))
    def update(self,force=False):
        now=time.monotonic()
        if not force and now-self.last_read_monotonic<self.minimum_interval:return
        self.last_read_monotonic=now
        try:
            value=self._read_value()
            if value is not None:self.last_distance_mm=value;self.last_updated_at=time.time();self.last_error=None
        except Exception as error:self.last_error=str(error)
    def status(self):
        self.update()
        out_of_range=self.last_distance_mm is not None and self.last_distance_mm>settings.DISTANCE_SENSOR_MAX_MM
        return {"available":True,"model":self.model,"address":f"0x{self.address:02X}","distance_mm":self.last_distance_mm,"out_of_range":out_of_range,"max_distance_mm":settings.DISTANCE_SENSOR_MAX_MM,"updated_at":self.last_updated_at,"error":self.last_error}
