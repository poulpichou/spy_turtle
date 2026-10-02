from robot.assets.assets import get_assets
from robot.shell.ui import colors,theme
from robot.shell.ui.widgets import draw_title,text

ROW_X=10
ROW_W=theme.WIDTH-20
ROW_H=52
ROW_GAP=8
COL_GAP=8
FIRST_Y=theme.CONTENT_Y+44
NAV_Y=theme.HEIGHT-theme.FOOTER_H-54

def inside(x,y,box):
    x0,y0,x1,y1=box
    return x0<=x<=x1 and y0<=y<=y1

def draw_button(draw,box,label,value=None,active=False,danger=False):
    x0,y0,x1,y1=box
    fill=(45,75,60) if active else (70,28,28) if danger else (30,30,38)
    outline=(90,170,125) if active else (170,70,70) if danger else theme.BORDER
    draw.rounded_rectangle(box,radius=theme.RADIUS,fill=fill,outline=outline,width=2)
    text(draw,x0+10,y0+14,label,15,colors.WHITE,True)
    if value is not None:
        bbox=draw.textbbox((0,0),str(value))
        text(draw,max(x0+10,x1-10-(bbox[2]-bbox[0])),y0+16,value,12,colors.GRAY)

def rows(count,start=FIRST_Y):
    return [(ROW_X,start+i*(ROW_H+ROW_GAP),ROW_X+ROW_W,start+i*(ROW_H+ROW_GAP)+ROW_H) for i in range(count)]

def grid(count,start=FIRST_Y,columns=2):
    width=(ROW_W-COL_GAP*(columns-1))//columns
    boxes=[]
    for index in range(count):
        row=index//columns;column=index%columns
        x0=ROW_X+column*(width+COL_GAP);y0=start+row*(ROW_H+ROW_GAP)
        boxes.append((x0,y0,x0+width,y0+ROW_H))
    return boxes

def navigation_boxes():
    third=(theme.WIDTH-24)//3
    return [(8,NAV_Y,8+third,NAV_Y+44),(12+third,NAV_Y,12+2*third,NAV_Y+44),(16+2*third,NAV_Y,theme.WIDTH-8,NAV_Y+44)]

class TouchView:
    interactive=True
    footer="TOUCH"
    def get_data(self,robot): return {}
    def close(self): pass
    def action_at(self,x,y): return None

class HomeView(TouchView):
    footer="HOME"
    def get_data(self,robot): return {"idle":robot.power.idle_mode}
    def draw(self,draw,display,data):
        draw_title(draw,"HOME")
        items=[("STATUS","status"),("LOGS","logs"),("COMMANDS","commands"),("ADMIN","admin"),("IDLE","idle")]
        self.hitboxes=[]
        for box,(label,action) in zip(grid(len(items)),items):
            value="ON" if action=="idle" and data.get("idle") else "OFF" if action=="idle" else None
            draw_button(draw,box,label,value,active=action=="idle" and data.get("idle"))
            self.hitboxes.append((box,action))
    def action_at(self,x,y):
        for box,action in getattr(self,"hitboxes",[]):
            if inside(x,y,box):return action

class CommandsView(TouchView):
    footer="COMMANDS"
    def draw(self,draw,display,data):
        draw_title(draw,"COMMANDS")
        items=[("FACE","faces"),("LEDS","leds"),("SCREEN","shell"),("SOUND","audio"),("←","back")]
        self.hitboxes=[]
        for box,(label,action) in zip(grid(len(items)),items):
            draw_button(draw,box,label)
            self.hitboxes.append((box,action))
    def action_at(self,x,y):
        for box,action in getattr(self,"hitboxes",[]):
            if inside(x,y,box):return action

class SelectionView(TouchView):
    PAGE_SIZE=10
    def __init__(self,section,page=0):
        self.section=section;self.page=max(0,int(page));self.footer=section.upper()
    def _items(self): return list(get_assets(self.section).items())
    def draw(self,draw,display,data):
        items=self._items();pages=max(1,(len(items)+self.PAGE_SIZE-1)//self.PAGE_SIZE);self.page=min(self.page,pages-1)
        draw_title(draw,f"{self.section.upper()} {self.page+1}/{pages}")
        current=items[self.page*self.PAGE_SIZE:(self.page+1)*self.PAGE_SIZE]
        self.hitboxes=[]
        for box,(name,asset) in zip(grid(len(current),theme.CONTENT_Y+40),current):
            draw_button(draw,box,asset.get("label",name))
            self.hitboxes.append((box,("select",name)))
        for box,label,action in zip(navigation_boxes(),("←","◀","▶"),("back","prev","next")):
            draw_button(draw,box,label)
            self.hitboxes.append((box,action))
    def action_at(self,x,y):
        for box,action in getattr(self,"hitboxes",[]):
            if inside(x,y,box):return action

class AdminView(TouchView):
    footer="ADMIN"
    def get_data(self,robot):
        volume=robot.speaker.volume if robot.speaker and hasattr(robot.speaker,"volume") else None
        return {"volume":volume,"idle":robot.power.idle_mode}
    def draw(self,draw,display,data):
        draw_title(draw,"ADMIN")
        self.hitboxes=[]
        volume_boxes=grid(2)
        draw_button(draw,volume_boxes[0],"VOL -",data.get("volume"));draw_button(draw,volume_boxes[1],"VOL +")
        self.hitboxes += [(volume_boxes[0],"volume_down"),(volume_boxes[1],"volume_up")]
        items=[("WI-FI","wifi"),("IDLE","idle"),("SHUTDOWN","shutdown"),("←","back")]
        for box,(label,action) in zip(grid(len(items),FIRST_Y+ROW_H+ROW_GAP),items):
            value="ON" if action=="idle" and data.get("idle") else "OFF" if action=="idle" else None
            draw_button(draw,box,label,value,active=action=="idle" and data.get("idle"),danger=action=="shutdown")
            self.hitboxes.append((box,action))
    def action_at(self,x,y):
        for box,action in getattr(self,"hitboxes",[]):
            if inside(x,y,box):return action

class WifiView(TouchView):
    PAGE_SIZE=8
    footer="WI-FI"
    def __init__(self,page=0): self.page=max(0,int(page))
    def get_data(self,robot):
        from robot.system.wifi import wifi_manager
        try:return wifi_manager.status()
        except Exception as error:return {"networks":[],"error":str(error)}
    def draw(self,draw,display,data):
        networks=data.get("networks",[]);pages=max(1,(len(networks)+self.PAGE_SIZE-1)//self.PAGE_SIZE);self.page=min(self.page,pages-1)
        draw_title(draw,f"KNOWN WI-FI {self.page+1}/{pages}")
        current=networks[self.page*self.PAGE_SIZE:(self.page+1)*self.PAGE_SIZE]
        self.hitboxes=[]
        for box,network in zip(grid(len(current),theme.CONTENT_Y+44),current):
            draw_button(draw,box,network.get("nickname") or network.get("ssid"),"ON" if network.get("active") else None,active=bool(network.get("active")))
            self.hitboxes.append((box,("wifi",network.get("ssid"))))
        if not current:text(draw,12,theme.CONTENT_Y+70,data.get("error") or "No saved Wi-Fi",14,colors.GRAY)
        for box,label,action in zip(navigation_boxes(),("←","◀","▶"),("back","prev","next")):
            draw_button(draw,box,label);self.hitboxes.append((box,action))
    def action_at(self,x,y):
        for box,action in getattr(self,"hitboxes",[]):
            if inside(x,y,box):return action

class ConfirmShutdownView(TouchView):
    footer="CONFIRM"
    def draw(self,draw,display,data):
        draw_title(draw,"SHUTDOWN?")
        text(draw,12,theme.CONTENT_Y+65,"Safely power off Spy Turtle?",15,colors.WHITE)
        self.cancel=(12,theme.CONTENT_Y+140,theme.WIDTH-12,theme.CONTENT_Y+200)
        self.confirm=(12,theme.CONTENT_Y+220,theme.WIDTH-12,theme.CONTENT_Y+280)
        draw_button(draw,self.cancel,"CANCEL")
        draw_button(draw,self.confirm,"SHUT DOWN",danger=True)
    def action_at(self,x,y):
        if inside(x,y,self.cancel):return "cancel"
        if inside(x,y,self.confirm):return "confirm"
