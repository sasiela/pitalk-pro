"""Explicit device restart confirmation."""
import threading
import queue
from PIL import Image,ImageDraw,ImageFont
from . import theme
from .wifi_ui import request

class RestartMenu:
    def __init__(self):
        self.index=0
        self.busy=False
        self.message=''
        self.results=queue.Queue()
        self.font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',15)
        self.small=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',12)
        self.title=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',20)
    def enter(self):
        self.index=0
        self.message=''
    def button(self,name):
        if self.busy:return False
        if name=='BACK':return True
        if name in ('UP','DOWN'):self.index=1-self.index
        if name=='ENTER':
            if self.index==0:return True
            self.busy=True
            self.message='Requesting restart...'
            def worker():
                try:r=request({'action':'restart_device','confirm':True})
                except Exception:r={'ok':False,'message':'Restart request failed.'}
                self.results.put(r)
            threading.Thread(target=worker,daemon=True).start()
        return False
    def poll(self):
        try:r=self.results.get_nowait()
        except queue.Empty:return False
        self.busy=bool(r.get('ok'))
        self.message=r.get('message','Restart request failed.')
        return True
    def render(self):
        img=Image.new('RGB',(240,320),theme.BG);d=ImageDraw.Draw(img)
        d.text((144,29),'Restart',font=self.title,fill=theme.TEXT,anchor='mm')
        d.line((12,46,228,46),fill=theme.LINE)
        d.rounded_rectangle((10,60,229,140),radius=8,fill=theme.PANEL)
        d.text((22,75),'Restart device?',font=self.font,fill=theme.TEXT)
        d.text((22,104),'Audio and Wi-Fi will stop.',font=self.small,fill=theme.MUTED)
        if self.busy:
            d.text((15,176),self.message,font=self.font,fill=theme.ACCENT)
        else:
            for i,label in enumerate(('Cancel','Restart')):
                y=161+43*i
                if i==self.index:
                    d.rounded_rectangle((10,y-4,229,y+29),radius=5,fill=theme.SELECTED)
                    d.rounded_rectangle((10,y,13,y+25),radius=1,fill=theme.ACCENT)
                d.text((23,y+3),label,font=self.font,fill=theme.TEXT)
            d.text((12,247),self.message,font=self.small,fill=theme.MUTED)
        d.line((12,273,228,273),fill=theme.LINE)
        theme.footer_icons(img,right='enter',enabled=not self.busy)
        return img
