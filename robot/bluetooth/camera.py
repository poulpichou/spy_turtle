"""Low-resolution JPEG snapshots over BLE GATT; one connected controller."""
from io import BytesIO
from threading import RLock
from PIL import Image
from robot.system.runtime import get_robot

class BLECamera:
    CHUNK=120
    def __init__(self):
        self.lock=RLock();self.frame=b"";self.offset=0;self.serial=0;self.header=True
    def write(self,value):
        with self.lock:
            if value==b"N":
                robot=get_robot()
                if robot is None or robot.camera is None:raise RuntimeError("Camera unavailable")
                raw=robot.camera.get_frame()
                with Image.open(BytesIO(raw)) as image:
                    image.thumbnail((160,120))
                    buffer=BytesIO();image.convert("RGB").save(buffer,format="JPEG",quality=35,optimize=True)
                    self.frame=buffer.getvalue()
                if len(self.frame)>65535:raise RuntimeError("BLE image too large")
                self.serial=(self.serial+1)&0xffff;self.offset=0;self.header=True
            elif len(value)==5 and value[0]==ord("C"):
                self.offset=int.from_bytes(value[1:],"little");self.header=False
            else:raise ValueError("Unknown BLE camera request")
    def read(self):
        with self.lock:
            if self.header:return len(self.frame).to_bytes(4,"little")+self.serial.to_bytes(2,"little")
            return self.frame[self.offset:self.offset+self.CHUNK]
