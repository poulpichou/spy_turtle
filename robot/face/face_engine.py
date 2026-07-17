import time

class FaceEngine:
    def __init__(self, renderer, library):
        self.renderer = renderer
        self.library = library

        self.current = None
        self.frame_index = 0
        self.frame_start = 0
        self.playing = False

    def play(self, name):
        sequence = self.library.get(name)

        if sequence is None:
            print(f"[FaceEngine] Unknown sequence: {name}")
            return

        self.current = sequence
        self.frame_index = 0
        self.frame_start = time.monotonic()
        self.playing = True

        self._show_current_frame()

    def update(self):
        if not self.playing:
            return

        frames = self.current["frames"]

        frame = frames[self.frame_index]

        elapsed = (time.monotonic() - self.frame_start) * 1000

        if elapsed < frame["duration"]:
            return

        self.frame_index += 1

        if self.frame_index >= len(frames):

            if self.current["loop"]:
                self.frame_index = 0
            else:
                self.playing = False

                if self.current["next"]:
                    self.play(self.current["next"])

                return

        self.frame_start = time.monotonic()
        self._show_current_frame()

    def _show_current_frame(self):
        frame = self.current["frames"][self.frame_index]

        left = self.library.get_eye(frame["left_eye"])
        right = self.library.get_eye(frame["right_eye"])

        if left is None or right is None:
            print("[FaceEngine] missing eye bitmap")
            return

        self.renderer.show(
            left_eye=left,
            right_eye=right
        )