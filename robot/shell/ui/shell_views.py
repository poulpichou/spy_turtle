import os
import shutil
from pathlib import Path
from PIL import Image,ImageOps
from robot.shell.ui import theme,colors
from robot.shell.ui.widgets import draw_title,draw_lines,text
from robot.utils.logger import log

IMAGE_EXTENSIONS={".png",".jpg",".jpeg",".bmp",".webp"}
GIF_EXTENSION=".gif"
ROOT=Path(__file__).resolve().parents[3]

def safe_call(function,default=None,digits=None):
    try:
        value=function()
        if digits is not None and isinstance(value,(int,float)):value=round(value,digits)
        return value
    except Exception:return default

def format_duration(seconds):
    seconds=max(0,int(seconds or 0))
    days,remaining=divmod(seconds,86400)
    hours,remaining=divmod(remaining,3600)
    minutes,seconds=divmod(remaining,60)
    if days:return f"{days}d {hours}h"
    if hours:return f"{hours}h {minutes}m"
    return f"{minutes}m {seconds}s"

def display_value(value,suffix=""): return "--" if value is None else f"{value}{suffix}"

class BaseView:
    title=""

    def __init__(self,footer=None): self.footer=footer or self.title
    def get_data(self,robot): return {}
    def draw(self,draw,display,data): pass
    def close(self): pass

class StatusView(BaseView):
    title="STATUS"

    def get_data(self,robot):
        disk=shutil.disk_usage(ROOT)
        servo=safe_call(robot.servo.status,{}) if robot.servo and hasattr(robot.servo,"status") else {}
        battery=robot.battery
        temperature=None
        temp_path=Path("/sys/class/thermal/thermal_zone0/temp")
        if temp_path.exists():temperature=round(float(temp_path.read_text().strip())/1000,1)
        uptime=None
        uptime_path=Path("/proc/uptime")
        if uptime_path.exists():uptime=float(uptime_path.read_text().split()[0])
        return [
            ("Uptime",format_duration(uptime)),
            ("CPU temperature",display_value(temperature," C")),
            ("System load",display_value(round(os.getloadavg()[0],2))),
            ("Disk free",display_value(round(disk.free/(1024**3),1)," GB")),
            ("Battery voltage",display_value(safe_call(battery.get_voltage,digits=2)," V")),
            ("Battery current",display_value(safe_call(battery.get_current,digits=2)," A")),
            ("Battery cells",display_value(safe_call(battery.get_cells))),
            ("Charging",self._yes_no(safe_call(battery.is_charging))),
            ("USB power",self._yes_no(safe_call(battery.usb_connected))),
            ("Robot mode",f"{robot.state.motion} / {robot.state.emotion}"),
            ("LED mode",robot.state.led_mode),
            ("Shell mode",robot.state.shell_mode),
            ("Head pan",self._servo(servo.get("pan"))),
            ("Head tilt",self._servo(servo.get("tilt")))
        ]

    @staticmethod
    def _yes_no(value): return "--" if value is None else "Yes" if value else "No"

    @staticmethod
    def _servo(axis):
        if not axis:return "--"
        current=display_value(axis.get("current"),"°")
        target=display_value(axis.get("target"),"°")
        return f"{current} -> {target}"

    def draw(self,draw,display,rows):
        draw_title(draw,"STATUS")
        start_y=theme.CONTENT_Y+40
        bottom=theme.HEIGHT-theme.FOOTER_H-4
        available=max(1,bottom-start_y)
        row_height=max(16,min(22,available//max(1,len(rows))))
        font_size=max(10,min(13,row_height-5))

        label_x=12
        separator_x=248
        value_x=266

        for index,(label,current) in enumerate(rows):
            y=start_y+index*row_height
            if y+row_height>bottom:break
            text(draw,label_x,y,label,font_size,colors.GRAY)
            draw.line(
                (separator_x,y-1,separator_x,y+row_height-3),
                fill=colors.GRAY,
                width=1
            )
            text(draw,value_x,y,current,font_size,colors.WHITE,True)

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
        with Image.open(self.path) as image:self.image=image.convert("RGB").copy()

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
            for index in range(getattr(image,"n_frames",1)):
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
        draw_lines(
            draw,
            wrap_text(self.message,28),
            theme.CONTENT_Y+45
        )

def media_view(path,footer=None):
    path=Path(path)
    extension=path.suffix.lower()
    if extension==GIF_EXTENSION:return GifView(path,footer)
    if extension in IMAGE_EXTENSIONS:return ImageView(path,footer)
    raise ValueError(f"Unsupported media format: {extension or 'none'}")

def fit_media(image):
    image=ImageOps.contain(
        image,
        (theme.WIDTH,theme.CONTENT_H)
    ).convert("RGB")
    canvas=Image.new(
        "RGB",
        (theme.WIDTH,theme.CONTENT_H),
        theme.CONTENT_BG
    )
    canvas.paste(
        image,
        (
            (theme.WIDTH-image.width)//2,
            (theme.CONTENT_H-image.height)//2
        )
    )
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