from picamera2 import Picamera2
import io

class Camera:
    def __init__(self):
        self.camera=Picamera2()
        self.camera.configure(self.camera.create_video_configuration(main={"size":(1280,720)}))
        self.running=False
        print("[Camera] ready")

    def start(self):
        if self.running: return
        self.camera.start()
        self.running=True
        print("[Camera] started")

    def stop(self):
        if not self.running: return
        self.camera.stop()
        self.running=False
        print("[Camera] stopped")

    def get_frame(self):
        if not self.running: self.start()

        stream=io.BytesIO()
        self.camera.capture_file(stream,format="jpeg")
        return stream.getvalue()

    def capture(self,path):
        if not self.running: self.start()
        self.camera.capture_file(path)