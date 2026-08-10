from io import BytesIO
from threading import RLock
from PIL import Image
from picamera2 import Picamera2
from robot.config import settings
from robot.utils.logger import log

class Camera:
    def __init__(self):
        self.lock=RLock();self.camera=None;self.running=False;self.enabled=True;self._create();log.info("[CAMERA] ready")
    def _create(self):
        if self.camera is not None:
            try:self.camera.close()
            except Exception:pass
        self.camera=Picamera2()
        self.camera.configure(self.camera.create_video_configuration(main={"size":(settings.CAMERA_WIDTH,settings.CAMERA_HEIGHT),"format":"RGB888"}))
        self.running=False
    def set_enabled(self,enabled):
        self.enabled=bool(enabled)
        if not self.enabled:self.stop()
        log.info(f"[CAMERA] {'enabled' if self.enabled else 'disabled'}")
        return self.enabled
    def start(self):
        with self.lock:
            if not self.enabled:raise RuntimeError("Camera disabled by Idle mode")
            if self.running:return
            try:self.camera.start()
            except RuntimeError as error:
                log.warn(f"[CAMERA] start failed, recreating camera: {error}");self._create();self.camera.start()
            self.running=True;log.info("[CAMERA] started")
    def stop(self):
        with self.lock:
            if not self.running:return
            try:self.camera.stop()
            finally:self.running=False
            log.info("[CAMERA] stopped")
    def get_frame(self):
        with self.lock:
            if not self.enabled:raise RuntimeError("Camera disabled by Idle mode")
            if not self.running:self.start()
            try:image=self.camera.capture_array()
            except RuntimeError as error:
                log.warn(f"[CAMERA] capture failed, recreating camera: {error}");self._create();self.camera.start();self.running=True;image=self.camera.capture_array()
            buffer=BytesIO();Image.fromarray(image).convert("RGB").save(buffer,format="JPEG",quality=85);return buffer.getvalue()
    def close(self):
        with self.lock:
            if self.camera is None:return
            try:
                if self.running:self.camera.stop()
            except Exception:pass
            try:self.camera.close()
            except Exception:pass
            self.running=False
