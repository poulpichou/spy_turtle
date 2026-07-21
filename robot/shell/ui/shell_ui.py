from PIL import ImageDraw
from robot.shell.ui import theme
from robot.shell.ui.widgets import draw_header,draw_footer

class ShellUI:
    def __init__(self,display): self.display=display

    def render(self):
        self.display.clear(theme.CONTENT_BG)
        return self.display.buffer,ImageDraw.Draw(self.display.buffer)

    def show(self): self.display.show()

    def show_view(self,view,data=None,state=None):
        _,draw=self.render()
        state=state or {}
        if not isinstance(state,dict): state=state.__dict__
        view.draw(draw,self.display,data)
        draw_header(draw,state)
        draw_footer(draw,view.footer)
        self.show()

    def image(self,path):
        self.display.load_image(path)
        self.display.show()