from robot.shell.ui import theme,colors
from robot.shell.ui.fonts import regular,bold,icons
from robot.shell.ui.icons import Icons

def text(draw,x,y,value,size=theme.TEXT_SIZE,color=colors.WHITE,b=False):
    draw.text((x,y),str(value),font=bold(size) if b else regular(size),fill=color)

def icon(draw,x,y,value,size=theme.ICON_SIZE,color=colors.WHITE):
    draw.text((x,y),value,font=icons(size),fill=color)

def box(draw,y,h,color):
    draw.rectangle([0,y,theme.WIDTH,y+h],fill=color)

def battery_color(level):
    return colors.RED if level<20 else colors.YELLOW if level<50 else colors.GREEN

def draw_header(draw,state):
    box(draw,0,theme.HEADER_H,theme.HEADER_BG)
    battery=state.get("battery","--")
    wifi=state.get("wifi","OK")
    emotion=state.get("emotion","neutral")
    try: level=int(battery)
    except: level=100
    icon(draw,8,10,Icons.BATTERY,16,battery_color(level))
    text(draw,30,12,f"{battery}%",12)
    icon(draw,82,10,Icons.WIFI,16,colors.WIFI)
    text(draw,104,12,wifi,12)
    icon(draw,155,10,Icons.FACE,16,colors.ACCENT)
    text(draw,180,12,emotion,12)

def draw_footer(draw,message="SPY TURTLE"):
    y=theme.HEIGHT-theme.FOOTER_H
    box(draw,y,theme.FOOTER_H,theme.FOOTER_BG)
    text(draw,8,y+8,message,theme.SMALL_SIZE,colors.GRAY)

def draw_title(draw,title):
    text(draw,theme.MARGIN,theme.CONTENT_Y+8,title,theme.TITLE_SIZE,colors.WHITE,True)

def draw_lines(draw,lines,start_y,size=theme.TEXT_SIZE,line_height=theme.LINE_HEIGHT,color=colors.WHITE):
    max_y=theme.HEIGHT-theme.FOOTER_H
    visible=max(0,(max_y-start_y)//line_height)
    lines=list(lines or [])[-visible:] if visible else []
    for index,line in enumerate(lines):
        text(draw,theme.MARGIN,start_y+index*line_height,line,size,color)
    return visible