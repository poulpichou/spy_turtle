"""Optional BLE vision streamer. One JPEG at a time; notifications are best-effort."""
import asyncio
from io import BytesIO
from PIL import Image
from robot.system.runtime import get_robot
from robot.utils.logger import log

class VisionStreamer:
    def __init__(self,server,service_uuid,char_uuid,chunk=60,interval=0.018):
        self.server=server;self.service_uuid=service_uuid;self.char_uuid=char_uuid
        self.chunk=chunk;self.interval=interval;self.task=None;self.serial=0
    def request(self,data):
        if data==b"X":
            if self.task and not self.task.done():self.task.cancel()
            return
        if data!=b"N":raise ValueError("Unknown BLE vision request")
        if self.task and not self.task.done():return # No queue of old frames.
        self.task=asyncio.create_task(self._stream())
    @staticmethod
    def _capture():
        robot=get_robot()
        if robot is None or robot.camera is None:raise RuntimeError("Camera unavailable")
        raw=robot.camera.get_frame()
        with Image.open(BytesIO(raw)) as image:
            image.thumbnail((160,120));buf=BytesIO()
            image.convert("RGB").save(buf,format="JPEG",quality=28,optimize=True)
            return buf.getvalue()
    async def _notify(self,data):
        # Bless sends the characteristic's current value when update_value is called.
        characteristic=self.server.get_characteristic(self.char_uuid)
        characteristic.value=bytearray(data)
        result=self.server.update_value(self.service_uuid,self.char_uuid)
        if asyncio.iscoroutine(result):await result
    async def _stream(self):
        try:
            jpeg=await asyncio.to_thread(self._capture)
            if len(jpeg)>65535:raise RuntimeError("BLE JPEG too large")
            self.serial=(self.serial+1)&65535;serial=self.serial.to_bytes(2,"little")
            await self._notify(b"H"+serial+len(jpeg).to_bytes(4,"little"))
            await asyncio.sleep(self.interval)
            for offset in range(0,len(jpeg),self.chunk):
                # Offset permits the browser to reject missing/out-of-order fragments.
                await self._notify(b"D"+serial+offset.to_bytes(2,"little")+jpeg[offset:offset+self.chunk])
                await asyncio.sleep(self.interval)
            log.info(f"[BLE VISION] frame={self.serial} bytes={len(jpeg)}")
        except asyncio.CancelledError:pass
        except Exception as error:log.error(f"[BLE VISION ERROR] {error}")
