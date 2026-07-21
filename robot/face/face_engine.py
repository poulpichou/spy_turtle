import time
from robot.utils.logger import log

class FaceEngine:
    def __init__(self,renderer,library):
        self.renderer=renderer
        self.library=library
        self.current_name=None
        self.current=None
        self.frame_index=0
        self.frame_start=0
        self.playing=False

    def play(self,name):
        sequence=self.library.get(name)
        if sequence is None:
            log.warn(f"[FACE] unknown sequence: {name}")
            return False
        if self.playing and not self.current.get("interruptible",True):
            return False
        self.current_name=name
        self.current=sequence
        self.frame_index=0
        self.frame_start=time.monotonic()
        self.playing=True
        log.info(f"[FACE] sequence {name}")
        self._show_current_frame()
        return True

    def update(self):
        if not self.playing or not self.current:return
        frame=self.current["frames"][self.frame_index]
        elapsed=(time.monotonic()-self.frame_start)*1000
        if elapsed<frame["duration"]:return
        self.frame_index+=1
        if self.frame_index>=len(self.current["frames"]):
            if self.current.get("loop",False):
                self.frame_index=0
            else:
                next_sequence=self.current.get("next")
                self.playing=False
                if next_sequence:self.play(next_sequence)
                return
        self.frame_start=time.monotonic()
        self._show_current_frame()

    def _show_current_frame(self):
        frame=self.current["frames"][self.frame_index]
        left=self.library.get_eye(frame["left_eye"])
        right=self.library.get_eye(frame["right_eye"])
        if left is None:
            log.warn(f"[FACE] missing eye: {frame['left_eye']}")
            return
        if right is None:
            log.warn(f"[FACE] missing eye: {frame['right_eye']}")
            return
        self.renderer.show(left_eye=left,right_eye=right)