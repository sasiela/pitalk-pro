"""PiTFT update menu; no network or privileged operations in the UI thread."""
import json,queue,socket,threading,time
from PIL import Image,ImageDraw,ImageFont
from . import theme

class UpdateMenu:
    def __init__(self):
        self.index=0;self.confirm=False;self.data={};self.results=queue.Queue();self.pending=False;self.last=0
        self.font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',15)
        self.small=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',12)
    def send(self,action):
        if self.pending:return
        self.pending=True
        def worker():
            try:
                with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM) as s:
                    s.settimeout(5);s.connect('/run/pitalk-update/control.sock')
                    s.sendall(json.dumps({'action':action,'confirm':action=='install'}).encode()+b'\n')
                    with s.makefile('rb') as f:r=json.loads(f.readline(8192))
            except Exception:r={'message':'Updater unavailable','ok':False}
            self.results.put(r)
        threading.Thread(target=worker,daemon=True).start()
    def enter(self):self.index=0;self.confirm=False;self.send('status')
    def poll(self):
        changed=False
        try:self.data=self.results.get_nowait();self.pending=False;changed=True
        except queue.Empty:pass
        if time.monotonic()-self.last>2:
            self.last=time.monotonic();self.send('status')
        return changed
    def button(self,name):
        if name=='BACK':
            if self.confirm:self.confirm=False;self.index=0;return False
            return True
        if self.pending or self.data.get('busy'):return False
        if name in ('UP','DOWN'):self.index=(self.index+(1 if name=='DOWN' else -1))%(2 if self.confirm else 3)
        elif name=='ENTER':
            if self.confirm:
                if self.index==1:self.send('install')
                self.confirm=False;self.index=0
            elif self.index==0:self.send('check')
            elif self.index==1:self.confirm=True;self.index=0
            else:return True
        return False
    def render(self):
        img=Image.new('RGB',(240,320),theme.BG);d=ImageDraw.Draw(img)
        d.text((14,18),'System / Update',font=self.font,fill=theme.TEXT)
        d.text((14,48),'Current: '+self.data.get('installed','...'),font=self.small,fill=theme.MUTED)
        d.text((14,67),'Latest: '+str(self.data.get('available') or 'Check first'),font=self.small,fill=theme.MUTED)
        labels=['Cancel','Install now'] if self.confirm else ['Check for updates','Install update','Back']
        if self.confirm:d.text((14,93),'Restart screen to update?',font=self.small,fill=theme.TEXT)
        for i,label in enumerate(labels):
            y=119+34*i
            if i==self.index:d.rounded_rectangle((10,y-3,230,y+26),radius=4,fill=theme.SELECTED)
            d.text((17,y),label,font=self.font,fill=theme.TEXT)
        message='Working...' if self.pending else self.data.get('message','')
        words=message.split();lines=['']
        for word in words:
            if len(lines[-1])+len(word)>28:lines.append('')
            lines[-1]+=(' ' if lines[-1] else '')+word
        for i,line in enumerate(lines[:3]):d.text((12,231+15*i),line,font=self.small,fill=theme.ACCENT)
        theme.footer_icons(img,right='enter',enabled=not self.data.get('busy'))
        return img
