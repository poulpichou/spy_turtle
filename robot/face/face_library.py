import json
from pathlib import Path


class FaceLibrary:
    def __init__(self):
        root = Path(__file__).parent.parent / "config" / "face"
        eyes_root = Path(__file__).parent.parent / "assets" / "eyes"

        with open(root / "eyes.json", encoding="utf-8") as f:
            self.eye_files = json.load(f)

        with open(root / "sequences.json", encoding="utf-8") as f:
            self.sequences = json.load(f)

        self.eyes = {}

        for name, filename in self.eye_files.items():
            path = eyes_root / filename
            self.eyes[name] = self._load_eye(path)

    def _load_eye(self, path):
        with open(path, encoding="utf-8") as f:
            lines = f.readlines()

        pixels = []

        for line in lines:
            line = line.strip()

            if not line or line.startswith("size:"):
                continue

            pixels.append(line)

        return pixels

    def get(self, name):
        return self.sequences.get(name)

    def get_eye(self, name):
        return self.eyes.get(name)