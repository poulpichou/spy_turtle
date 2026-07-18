from picamera2 import Picamera2
from io import BytesIO
from PIL import Image


class Camera:
    def __init__(self):
        self.camera=Picamera2()
        self.running=False
        self.camera.configure(self.camera.create_video_configuration(main={"size":(1280,720),"format":"RGB888"}))
        print("[Camera] ready")

    def start(self):
        if not self.running:
            self.camera.start()
            self.running=True
            print("[Camera] started")

    def stop(self):
        if self.running:
            self.camera.stop()
            self.running=False
            print("[Camera] stopped")

    def get_frame(self):
        if not self.running:
            self.start()

        image=self.camera.capture_array()
        img=Image.fromarray(image).convert("RGB")

        buffer=BytesIO()
        img.save(buffer,format="JPEG",quality=85)

        return buffer.getvalue()