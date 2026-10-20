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
    def status(self):
        self.update();return {"available":True,"model":"BME680","address":f"0x{self.address:02X}",**self.last_values,"updated_at":self.last_updated_at,"error":self.last_error}
