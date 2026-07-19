from pathlib import Path
from PIL import ImageFont

FONT_DIR=Path(__file__).parent.parent.parent/"assets"/"fonts"

def load(name,size):
    return ImageFont.truetype(FONT_DIR/name,size)

REGULAR="Roboto-Regular.ttf"
BOLD="Roboto-Bold.ttf"
ICONS="Font Awesome 7 Free-Solid-900.otf"

def regular(size): return load(REGULAR,size)
def bold(size): return load(BOLD,size)
def icons(size): return load(ICONS,size)