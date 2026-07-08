from flask import Flask, Response
from software.hardware.camera import Camera
import time

app = Flask(__name__)

camera = Camera()
camera.start()


@app.route("/stream")
def stream():
    def generate():
        while True:
            frame = camera.get_frame()

            if frame:
                yield f"data:{frame}\n\n"

            time.sleep(0.1)

    return Response(generate(), mimetype="text/event-stream")


@app.route("/")
def index():
    return {
        "status": "Spy Turtle camera running",
        "endpoints": ["/stream"]
    }


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)