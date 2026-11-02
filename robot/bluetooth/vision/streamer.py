"""Optional BLE vision streamer. One JPEG at a time; notifications are best-effort."""
import asyncio
from io import BytesIO
from time import perf_counter
from PIL import Image
from robot.system.runtime import get_robot
from robot.config import settings
from robot.utils.logger import log

class VisionStreamer:
    def __init__(self,server,service_uuid,char_uuid,chunk=60,interval=0.018):
        self.server=server;self.service_uuid=service_uuid;self.char_uuid=char_uuid
        self.chunk=int(chunk);self.interval=interval;self.task=None;self.serial=0
        if not 1<=self.chunk<=240:raise ValueError("BLE vision chunk must be 1..240")
        log.info(f"[BLE VISION CONFIG] chunk={self.chunk} interval_ms={self.interval*1000:.1f} size={settings.BLUETOOTH_VISION_WIDTH}x{settings.BLUETOOTH_VISION_HEIGHT} quality={settings.BLUETOOTH_VISION_QUALITY}")
    def request(self,data):
        if data==b"X":
            if self.task and not self.task.done():self.task.cancel()
            return
        if data!=b"N":raise ValueError("Unknown BLE vision request")
        if self.task and not self.task.done():return # No queue of old frames.
        self.task=asyncio.create_task(self._stream())
    @staticmethod
    def _capture():
        t0=perf_counter()
        robot=get_robot()
        if robot is None or robot.camera is None:raise RuntimeError("Camera unavailable")
        raw=robot.camera.get_frame()
        t1=perf_counter()
        with Image.open(BytesIO(raw)) as image:
            image.thumbnail((settings.BLUETOOTH_VISION_WIDTH,settings.BLUETOOTH_VISION_HEIGHT));buf=BytesIO()
            image.convert("RGB").save(buf,format="JPEG",quality=settings.BLUETOOTH_VISION_QUALITY,optimize=True)
            jpeg=buf.getvalue()
        t2=perf_counter()
        return jpeg,(t1-t0)*1000,(t2-t1)*1000,len(raw)
    async def _notify(self,data):
        # Bless sends the characteristic's current value when update_value is called.
        characteristic=self.server.get_characteristic(self.char_uuid)
        characteristic.value=bytearray(data)
        result=self.server.update_value(self.service_uuid,self.char_uuid)
        if asyncio.iscoroutine(result):await result
    async def _stream(self):
        start=perf_counter();stage="capture";chunks=0;notify_ms=0.0;sleep_ms=0.0
        try:
            jpeg,capture_ms,encode_ms,raw_bytes=await asyncio.to_thread(self._capture)
            prepared=perf_counter();stage="send"
            if len(jpeg)>65535:raise RuntimeError("BLE JPEG too large")
            self.serial=(self.serial+1)&65535;serial=self.serial.to_bytes(2,"little")
            t=perf_counter()
            await self._notify(b"H"+serial+len(jpeg).to_bytes(4,"little"))
            notify_ms+=(perf_counter()-t)*1000
            t=perf_counter();await asyncio.sleep(self.interval);sleep_ms+=(perf_counter()-t)*1000
            for offset in range(0,len(jpeg),self.chunk):
                t=perf_counter()
                await self._notify(b"D"+serial+offset.to_bytes(2,"little")+jpeg[offset:offset+self.chunk])
                notify_ms+=(perf_counter()-t)*1000;chunks+=1
                t=perf_counter();await asyncio.sleep(self.interval);sleep_ms+=(perf_counter()-t)*1000
            end=perf_counter()
            log.info(f"[BLE VISION] frame={self.serial} bytes={len(jpeg)}")
            log.info(f"[BLE PERF] frame={self.serial} jpeg={len(jpeg)} raw={raw_bytes} chunks={chunks} chunk_size={self.chunk} interval_ms={self.interval*1000:.1f} capture_ms={capture_ms:.1f} encode_ms={encode_ms:.1f} prep_ms={(prepared-start)*1000:.1f} notify_ms={notify_ms:.1f} sleep_ms={sleep_ms:.1f} send_ms={(end-prepared)*1000:.1f} total_ms={(end-start)*1000:.1f}")
        except asyncio.CancelledError:
            log.info(f"[BLE PERF] cancelled stage={stage} chunks={chunks} elapsed_ms={(perf_counter()-start)*1000:.1f}")
            raise
        except Exception as error:log.error(f"[BLE VISION ERROR] stage={stage} chunks={chunks} elapsed_ms={(perf_counter()-start)*1000:.1f} {error}")
