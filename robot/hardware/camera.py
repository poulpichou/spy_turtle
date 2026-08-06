from io import BytesIO
from threading import RLock

from PIL import Image
from picamera2 import Picamera2

from robot.config import settings
from robot.utils.logger import log

class Camera:
    def __init__(self):
        self.camera=Picamera2()
        self.running=False
        self.lock=RLock()
        self.camera.configure(self.camera.create_video_configuration(main={"size":(settings.CAMERA_WIDTH,settings.CAMERA_HEIGHT),"format":"RGB888"}))
        log.info("[CAMERA] ready")

    def start(self):
        with self.lock:
            if self.running:return
            self.camera.start()
            self.running=True
            log.info("[CAMERA] started")

    def stop(self):
        with self.lock:
            if not self.running:return
            self.camera.stop()
            self.running=False
            log.info("[CAMERA] stopped")

    def get_frame(self):
        with self.lock:
            if not self.running:self.start()
            try:image=self.camera.capture_array()
            except RuntimeError as error:
                log.warn(f"[CAMERA] capture failed, restarting: {error}")
                try:self.camera.stop()
                except Exception:pass
                self.running=False
                self.start()
                image=self.camera.capture_array()
            buffer=BytesIO()
            Image.fromarray(image).convert("RGB").save(buffer,format="JPEG",quality=85)
            return buffer.getvalue()
