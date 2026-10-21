import time
from robot.config import settings
from robot.utils.logger import log

class EnvironmentSensor:
    def __init__(self):
        import adafruit_bme680,board
        self.i2c=board.I2C();self.address=settings.BME680_ADDRESS;self.minimum_interval=settings.BME680_UPDATE_INTERVAL
        self.last_read_monotonic=0.0;self.last_updated_at=None;self.last_values={"temperature_c":None,"humidity_percent":None,"pressure_hpa":None,"gas_ohms":None};self.last_error=None
        self.sensor=adafruit_bme680.Adafruit_BME680_I2C(self.i2c,address=self.address);log.info(f"[ENVIRONMENT] BME680 ready address=0x{self.address:02X}")
    def update(self,force=False):
        now=time.monotonic()
        if not force and now-self.last_read_monotonic<self.minimum_interval:return
        self.last_read_monotonic=now
        try:
            self.last_values={"temperature_c":round(float(self.sensor.temperature),1),"humidity_percent":round(float(self.sensor.relative_humidity),1),"pressure_hpa":round(float(self.sensor.pressure),1),"gas_ohms":round(float(self.sensor.gas),0)};self.last_updated_at=time.time();self.last_error=None
        except Exception as error:self.last_error=str(error)
    @staticmethod
    def _air_quality(gas_ohms):
        if gas_ohms is None:return None
        points=sorted(settings.BME680_AIR_QUALITY_POINTS,key=lambda point:point[1])
        if gas_ohms<=points[0][1]:return float(points[0][0])
        if gas_ohms>=points[-1][1]:return float(points[-1][0])
        for (score1,ohms1),(score2,ohms2) in zip(points,points[1:]):
            if ohms1<=gas_ohms<=ohms2:
                score=score1+(gas_ohms-ohms1)*(score2-score1)/(ohms2-ohms1)
                return round(float(score),1)
        return None
    def status(self):
        self.update()
        pressure=self.last_values.get("pressure_hpa");gas=self.last_values.get("gas_ohms")
        return {"available":True,"model":"BME680","address":f"0x{self.address:02X}",**self.last_values,"pressure_atm":None if pressure is None else round(float(pressure)/1013.25,3),"air_quality":self._air_quality(gas),"updated_at":self.last_updated_at,"error":self.last_error}
