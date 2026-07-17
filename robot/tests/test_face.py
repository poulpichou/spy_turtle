import time

from robot.face.face_controller import FaceController
from robot.face.eyes_renderer import EyesRenderer
from robot.simulation.fake_eyes_display import FakeEyesDisplay


def wait(face, seconds):
    end = time.monotonic() + seconds

    while time.monotonic() < end:
        face.update()
        time.sleep(0.02)


def main():
    left = FakeEyesDisplay("left")
    right = FakeEyesDisplay("right")

    renderer = EyesRenderer(left, right)
    face = FaceController(renderer)

    print("[Test] neutral")
    face.neutral()
    wait(face, 1)

    print("[Test] blink")
    face.blink()
    wait(face, 1)

    print("[Test] look left")
    face.look_left()
    wait(face, 1)

    print("[Test] look right")
    face.look_right()
    wait(face, 1)

    print("[Test] yawn")
    face.yawn()
    wait(face, 3)


if __name__ == "__main__":
    main()