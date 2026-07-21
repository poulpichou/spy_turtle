from pathlib import Path
from PIL import Image,ImageOps
from robot.shell.ui import theme
from robot.shell.ui.widgets import draw_title,draw_lines
from robot.utils.logger import log

IMAGE_EXTENSIONS={".png",".jpg",".jpeg",".bmp",".webp"}
GIF_EXTENSION=".gif"

class BaseView:
    title=""

    def __init__(self,footer=None): self.footer=footer or self.title
    def get_data(self,robot): return {}
    def draw(self,draw,display,data): pass
    def close(self): pass

class StatusView(BaseView):
    title="STATUS"

    def get_data(self,robot): return robot.state.__dict__

    def draw(self,draw,display,data):
        draw_title(draw,"SPY TURTLE")
        draw_lines(draw,[
            f"Battery  {data.get('battery','--')}%",
            f"Camera   {data.get('camera_on','--')}",
            f"Audio    {data.get('sound','--')}",
            f"LED      {data.get('led_mode','--')}",
            f"Move     {data.get('motion','--')}",
            f"Face     {data.get('emotion','--')}"
        ],theme.CONTENT_Y+45)

class LogView(BaseView):
    title="LOG"

    def get_data(self,robot): return log.tail(100)

    def draw(self,draw,display,lines):
        draw_title(draw,"LOG")
        draw_lines(
            draw,
            lines,
            theme.CONTENT_Y+42,
            size=theme.SMALL_SIZE,
            line_height=18
        )

class ImageView(BaseView):
    title="IMAGE"

    def __init__(self,path,footer=None):
        super().__init__(footer or Path(path).name)
        self.path=Path(path)
        with Image.open(self.path) as image:
            self.image=image.convert("RGB").copy()

    def draw(self,draw,display,data):
        display.buffer.paste(fit_media(self.image),(0,theme.CONTENT_Y))

class GifView(BaseView):
    title="GIF"

    def __init__(self,path,footer=None):
        super().__init__(footer or Path(path).name)
        self.path=Path(path)
        self.frames=[]
        self.durations=[]
        self.frame_index=0
        with Image.open(self.path) as image:
            frame_count=getattr(image,"n_frames",1)
            for index in range(frame_count):
                image.seek(index)
                self.frames.append(image.convert("RGB").copy())
                self.durations.append(max(20,image.info.get("duration",100)))
        self.duration=self.durations[0] if self.durations else 100

    def draw(self,draw,display,data):
        if not self.frames:return
        frame=self.frames[self.frame_index]
        self.duration=self.durations[self.frame_index]
        display.buffer.paste(fit_media(frame),(0,theme.CONTENT_Y))
        self.frame_index=(self.frame_index+1)%len(self.frames)

    def close(self):
        self.frames.clear()
        self.durations.clear()

class TextView(BaseView):
    title="MESSAGE"

    def __init__(self,message,footer=None):
        super().__init__(footer or self.title)
        self.message=str(message)

    def draw(self,draw,display,data):
        draw_title(draw,"MESSAGE")
        draw_lines(draw,wrap_text(self.message,28),theme.CONTENT_Y+45)

def media_view(path,footer=None):
    path=Path(path)
    extension=path.suffix.lower()
    if extension==GIF_EXTENSION:return GifView(path,footer)
    if extension in IMAGE_EXTENSIONS:return ImageView(path,footer)
    raise ValueError(f"Unsupported media format: {extension or 'none'}")

def fit_media(image):
    image=ImageOps.contain(image,(theme.WIDTH,theme.CONTENT_H)).convert("RGB")
    canvas=Image.new("RGB",(theme.WIDTH,theme.CONTENT_H),theme.CONTENT_BG)
    x=(theme.WIDTH-image.width)//2
    y=(theme.CONTENT_H-image.height)//2
    canvas.paste(image,(x,y))
    return canvas

def wrap_text(value,width):
    words=str(value).split()
    lines=[]
    current=""
    for word in words:
        candidate=f"{current} {word}".strip()
        if len(candidate)<=width:
            current=candidate
        else:
            if current:lines.append(current)
            current=word
    if current:lines.append(current)
    return lines