from threading import RLock
from PIL import ImageDraw
from robot.shell.ui import theme
from robot.shell.ui.widgets import draw_header,draw_footer

class ShellUI:
    def __init__(self,display):
        self.display=display
        self.lock=RLock()

    def render(self):
        self.display.clear(theme.CONTENT_BG)
        return self.display.buffer,ImageDraw.Draw(self.display.buffer)

    def show(self):
        import time
        from robot.shell.diagnostics import trace
        with self.lock:
            start=time.monotonic()
            try:self.display.show()
            except Exception as error:
                trace('errors',operation='spi',error=repr(error))
                raise
            trace('spi',duration_ms=round((time.monotonic()-start)*1000,1))

    def show_view(self,view,data=None,state=None):
        from robot.shell.diagnostics import trace
        with self.lock:
            trace('render',view=type(view).__name__)
            _,draw=self.render()
            state=state or {}
            if not isinstance(state,dict):state=state.__dict__
            view.draw(draw,self.display,data)
            draw_header(draw,state)
            draw_footer(draw,view.footer)
            self.show()

    def image(self,path):
        with self.lock:
            self.display.load_image(path)
            self.show()
