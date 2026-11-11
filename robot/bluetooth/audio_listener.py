# Low-bandwidth BLE microphone stream, G.711 mu-law 8 kHz.
import asyncio
from robot.config import settings
from robot.utils.logger import log

class BleAudioListener:
    def __init__(self,server,service_uuid,char_uuid):
        self.server=server;self.service_uuid=service_uuid;self.char_uuid=char_uuid;self.task=None
    def request(self,raw):
        if raw==b"Q":self.stop()
        elif raw==b"L" and (self.task is None or self.task.done()):self.task=asyncio.create_task(self._stream())
    def stop(self):
        if self.task and not self.task.done():self.task.cancel()
    @staticmethod
    def encode(sample):
        sign=0x80 if sample<0 else 0
        magnitude=min(32635,abs(sample)+132)
        exponent=7
        mask=0x4000
        while exponent>0 and not (magnitude&mask):exponent-=1;mask>>=1
        mantissa=(magnitude>>(exponent+3))&15
        return (~(sign|(exponent<<4)|mantissa))&255
    async def _stream(self):
        process=None
        try:
            command=["arecord","-q","-D",settings.MICROPHONE_DEVICE,"-f","S16_LE","-r","16000","-c","1","-t","raw"]
            process=await asyncio.create_subprocess_exec(*command,stdout=asyncio.subprocess.PIPE,stderr=asyncio.subprocess.DEVNULL)
            log.info("[BLE LISTEN] started")
            while True:
                pcm=await process.stdout.readexactly(640) # 20 ms at 16 kHz, downsample to 8 kHz
                samples=[int.from_bytes(pcm[i:i+2],"little",signed=True) for i in range(0,len(pcm),4)]
                packet=b"D"+bytes(self.encode(sample) for sample in samples)
                characteristic=self.server.get_characteristic(self.char_uuid)
                characteristic.value=bytearray(packet)
                result=self.server.update_value(self.service_uuid,self.char_uuid)
                if asyncio.iscoroutine(result):await result
                await asyncio.sleep(0.002)
        except asyncio.CancelledError:pass
        except asyncio.IncompleteReadError:log.warn("[BLE LISTEN] microphone stream ended")
        except Exception as error:log.error(f"[BLE LISTEN] {error}")
        finally:
            if process and process.returncode is None:
                process.terminate()
                try:await asyncio.wait_for(process.wait(),timeout=1)
                except asyncio.TimeoutError:process.kill();await process.wait()
            log.info("[BLE LISTEN] stopped")
