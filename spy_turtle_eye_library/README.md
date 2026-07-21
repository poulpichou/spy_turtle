# Spy Turtle eye library update

Copy the `robot` directory over the repository's existing `robot` directory, then run from the repository root:

```bash
python update_assets.py
rm update_assets.py
```

This package:
- adds mirrored angry eye assets;
- fixes `FaceEngine` to load eye bitmaps through `get_eye()`;
- restores animated blink, double blink, look and yawn sequences;
- restores weighted idle facial behaviour;
- updates `assets.json` with the two new eye assets.
