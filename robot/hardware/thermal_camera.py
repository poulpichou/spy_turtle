import time
from io import BytesIO
from threading import Event,Lock,Thread
from PIL import Image,ImageDraw
from robot.config import settings
from robot.utils.logger import log

class ThermalCamera:
    SENSOR_WIDTH=32
    SENSOR_HEIGHT=24
    PIXELS=SENSOR_WIDTH*SENSOR_HEIGHT
    ACTIVE_WINDOW_SECONDS=2.0

    def __init__(self):
        import adafruit_mlx90640
        import board
        import busio
        if settings.THERMAL_ROTATION not in (0,90,180,270):raise ValueError("THERMAL_ROTATION must be 0, 90, 180 or 270")
        self.adafruit_mlx90640=adafruit_mlx90640
        self.frame=[0.0]*self.PIXELS
        self.cache_lock=Lock()
        self.latest_jpeg=self._placeholder("Thermal warming up")
        self.last_frame=None
        self.last_error=None
        self.last_min=None
        self.last_max=None
        self.requested_until=0.0
        self.stop_event=Event()
        self.i2c=busio.I2C(board.SCL,board.SDA,frequency=settings.THERMAL_I2C_FREQUENCY)
        self.sensor=adafruit_mlx90640.MLX90640(self.i2c,address=settings.THERMAL_CAMERA_ADDRESS)
        self.sensor.refresh_rate=self._refresh_rate(settings.THERMAL_REFRESH_RATE_HZ)
        self.worker=Thread(target=self._run,name="thermal-camera",daemon=True)
        self.worker.start()
        log.info(f"[THERMAL] MLX90640 ready address=0x{settings.THERMAL_CAMERA_ADDRESS:02X} refresh={settings.THERMAL_REFRESH_RATE_HZ}Hz rotation={settings.THERMAL_ROTATION} flip_vertical={settings.THERMAL_FLIP_VERTICAL} nonblocking=true")

    def _refresh_rate(self,hz):
        rates={0.5:self.adafruit_mlx90640.RefreshRate.REFRESH_0_5_HZ,1:self.adafruit_mlx90640.RefreshRate.REFRESH_1_HZ,2:self.adafruit_mlx90640.RefreshRate.REFRESH_2_HZ,4:self.adafruit_mlx90640.RefreshRate.REFRESH_4_HZ,8:self.adafruit_mlx90640.RefreshRate.REFRESH_8_HZ,16:self.adafruit_mlx90640.RefreshRate.REFRESH_16_HZ,32:self.adafruit_mlx90640.RefreshRate.REFRESH_32_HZ,64:self.adafruit_mlx90640.RefreshRate.REFRESH_64_HZ}
        return rates.get(hz,rates[2])

    def _run(self):
        while not self.stop_event.is_set():
            if time.monotonic()>self.requested_until:
                self.stop_event.wait(0.05)
                continue
            try:
                values=self._read_temperatures()
                image=self._image(values)
                buffer=BytesIO()
                image.save(buffer,format="JPEG",quality=settings.THERMAL_JPEG_QUALITY)
                with self.cache_lock:
                    self.latest_jpeg=buffer.getvalue()
                    self.last_frame=time.time()
                    self.last_min=round(min(values),1)
                    self.last_max=round(max(values),1)
                    self.last_error=None
            except Exception as error:
                with self.cache_lock:self.last_error=str(error)
                log.warn(f"[THERMAL] background frame failed: {error}")
                self.stop_event.wait(0.1)

    def _read_temperatures(self):
        error=None
        for _ in range(4):
            try:
                self.sensor.getFrame(self.frame)
                return list(self.frame)
            except (ValueError,RuntimeError) as exc:
                error=exc
                time.sleep(0.02)
        raise RuntimeError(f"MLX90640 frame read failed: {error}") from error

    @staticmethod
    def _range(values):
        ordered=sorted(v for v in values if -100<v<500)
        if not ordered:return 20.0,40.0
        low=ordered[max(0,int(len(ordered)*0.05)-1)]
        high=ordered[min(len(ordered)-1,int(len(ordered)*0.95))]
        if high-low<2:
            center=(high+low)/2
            return center-1,center+1
        return low,high

    @staticmethod
    def _palette(value):
        stops=((0.00,(0,0,0)),(0.20,(45,0,75)),(0.42,(145,0,85)),(0.62,(230,35,25)),(0.80,(255,145,0)),(0.93,(255,235,60)),(1.00,(255,255,255)))
        value=max(0.0,min(1.0,value))
        for index in range(1,len(stops)):
            p1,c1=stops[index-1];p2,c2=stops[index]
            if value<=p2:
                ratio=(value-p1)/(p2-p1)
                return tuple(round(c1[i]+(c2[i]-c1[i])*ratio) for i in range(3))
        return stops[-1][1]

    @staticmethod
    def _transform(image):
        rotation=settings.THERMAL_ROTATION
        if rotation==90:image=image.transpose(Image.Transpose.ROTATE_90)
        elif rotation==180:image=image.transpose(Image.Transpose.ROTATE_180)
        elif rotation==270:image=image.transpose(Image.Transpose.ROTATE_270)
        if settings.THERMAL_FLIP_VERTICAL:image=image.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
        return image

    def _image(self,values):
        low,high=self._range(values)
        scale=max(0.001,high-low)
        pixels=[self._palette((value-low)/scale) for value in values]
        image=Image.new("RGB",(self.SENSOR_WIDTH,self.SENSOR_HEIGHT))
        image.putdata(pixels)
        image=self._transform(image)
        image=image.resize((settings.THERMAL_OUTPUT_WIDTH,settings.THERMAL_OUTPUT_HEIGHT),Image.Resampling.BICUBIC)
        draw=ImageDraw.Draw(image)
        minimum=min(values);maximum=max(values);center=values[(self.SENSOR_HEIGHT//2)*self.SENSOR_WIDTH+self.SENSOR_WIDTH//2]
        text=f"{minimum:.1f}C  center {center:.1f}C  max {maximum:.1f}C"
        box=draw.textbbox((0,0),text)
        draw.rectangle((4,4,box[2]+10,box[3]+10),fill=(0,0,0))
        draw.text((7,6),text,fill=(255,255,255))
        return image

    def _placeholder(self,text):
        image=Image.new("RGB",(settings.THERMAL_OUTPUT_WIDTH,settings.THERMAL_OUTPUT_HEIGHT),(20,20,20))
        draw=ImageDraw.Draw(image)
        box=draw.textbbox((0,0),text)
        x=max(0,(settings.THERMAL_OUTPUT_WIDTH-(box[2]-box[0]))//2)
        y=max(0,(settings.THERMAL_OUTPUT_HEIGHT-(box[3]-box[1]))//2)
        draw.text((x,y),text,fill=(255,255,255))
        buffer=BytesIO()
        image.save(buffer,format="JPEG",quality=80)
        return buffer.getvalue()

    def get_frame(self):
        self.requested_until=time.monotonic()+self.ACTIVE_WINDOW_SECONDS
        with self.cache_lock:return self.latest_jpeg

    def status(self):
        with self.cache_lock:
            return {"available":True,"model":"MLX90640","address":f"0x{settings.THERMAL_CAMERA_ADDRESS:02X}","sensor_size":[self.SENSOR_WIDTH,self.SENSOR_HEIGHT],"output_size":[settings.THERMAL_OUTPUT_WIDTH,settings.THERMAL_OUTPUT_HEIGHT],"refresh_rate_hz":settings.THERMAL_REFRESH_RATE_HZ,"rotation":settings.THERMAL_ROTATION,"flip_vertical":settings.THERMAL_FLIP_VERTICAL,"last_frame_at":self.last_frame,"min_c":self.last_min,"max_c":self.last_max,"error":self.last_error}

    def close(self):
        self.stop_event.set()
        if self.worker.is_alive():self.worker.join(timeout=2.0)
        try:self.i2c.deinit()
        except Exception:pass
