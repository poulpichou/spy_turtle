from PIL import ImageDraw
from robot.shell.ui import theme
from robot.shell.ui.widgets import draw_header,draw_footer,draw_title,draw_lines


class ShellUI:
    def __init__(self,display):
        self.display=display

    def render(self):
        self.display.clear(theme.CONTENT_BG)
        return self.display.buffer,ImageDraw.Draw(self.display.buffer)

    def show(self):
        self.display.show()

    def status(self,state):
        image,draw=self.render()

        data=state if isinstance(state,dict) else state.__dict__

        draw_header(draw,data)

        draw_title(draw,"SPY TURTLE")

        lines=[
            f"Battery  {data.get('battery','--')}%",
            f"Camera   {data.get('camera','--')}",
            f"Audio    {data.get('sound','--')}",
            f"LED      {data.get('led_mode','--')}",
            f"Move     {data.get('motion','--')}",
            f"Face     {data.get('emotion','--')}"
        ]

        draw_lines(
            draw,
            lines,
            theme.CONTENT_Y+45
        )

        draw_footer(draw,"STATUS")
        self.show()

    def message(self,text,color=None):
        image,draw=self.render()

        draw_header(draw,{})

        draw_title(draw,"MESSAGE")

        y=theme.CONTENT_Y+45

        for line in str(text).split("\n"):
            draw.text(
                (theme.MARGIN,y),
                line,
                font=self.display.font,
                fill=color or (255,255,255)
            )
            y+=theme.LINE_HEIGHT

        draw_footer(draw,"MESSAGE")
        self.show()

    def log(self,lines):
        image,draw=self.render()

        draw_header(draw,{})

        draw_title(draw,"LOG")

        draw_lines(
            draw,
            lines[-10:],
            theme.CONTENT_Y+45
        )

        draw_footer(draw,"LOG")
        self.show()

    def image(self,path):
        self.display.load_image(path)
        self.display.show()