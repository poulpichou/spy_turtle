import math
import time
from io import BytesIO
from PIL import Image,ImageDraw
from robot.config import settings

class FakeThermalCamera:
    def __init__(self):self.last_frame=None

    def get_frame(self):
        width,height=32,24
        now=time.time()
        cx=16+8*math.sin(now/2);cy=12+5*math.cos(now/3)
        values=[]
        for y in range(height):
            for x in range(width):
                distance=(x-cx)**2+(y-cy)**2
                values.append(22+16*math.exp(-distance/20))
        low,high=min(values),max(values)
        image=Image.new("RGB",(width,height))
        pixels=[]
        for value in values:
            p=(value-low)/(high-low)
            pixels.append((round(255*p),round(255*max(0,p-0.35)/0.65),round(80*max(0,p-0.75)/0.25)))
        image.putdata(pixels)
        image=image.resize((settings.THERMAL_OUTPUT_WIDTH,settings.THERMAL_OUTPUT_HEIGHT),Image.Resampling.BICUBIC)
        draw=ImageDraw.Draw(image);draw.text((7,6),f"SIM  {low:.1f}C - {high:.1f}C",fill=(255,255,255))
        buffer=BytesIO();image.save(buffer,format="JPEG",quality=settings.THERMAL_JPEG_QUALITY)
        self.last_frame=time.time()
        return buffer.getvalue()

    def status(self):
        return {"available":True,"model":"simulated","address":None,"sensor_size":[32,24],"output_size":[settings.THERMAL_OUTPUT_WIDTH,settings.THERMAL_OUTPUT_HEIGHT],"refresh_rate_hz":settings.THERMAL_REFRESH_RATE_HZ,"last_frame_at":self.last_frame,"min_c":None,"max_c":None,"error":None}

    def close(self):pass
