from robot.shell.ui import theme
from robot.shell.ui.widgets import draw_title,draw_lines
from PIL import ImageDraw


class BaseView:
    title=""
    def __init__(self,footer=None):
        self.footer=footer or self.title

    def draw(self,draw,display,data): pass


class StatusView(BaseView):
    title="STATUS"
    def draw(self,draw,display,data):
        draw_title(draw,"SPY TURTLE")
        lines=[
            f"Battery  {data.get('battery','--')}%",
            f"Camera   {data.get('camera','--')}",
            f"Audio    {data.get('sound','--')}",
            f"LED      {data.get('led_mode','--')}",
            f"Move     {data.get('motion','--')}",
            f"Face     {data.get('emotion','--')}"
        ]
        draw_lines(draw,lines,theme.CONTENT_Y+45)


class LogView(BaseView):
    title="LOG"

    def draw(self,draw,display,lines):
        draw_title(draw,"LOG")
        draw_lines(draw,lines,theme.CONTENT_Y+45)

