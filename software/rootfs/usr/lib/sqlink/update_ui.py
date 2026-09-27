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
        img=Image.new('RGB',(240,320),theme.BG)
        d=theme.MenuDraw(img)
        d.text((144,29),'System Update',font=self.font,fill=theme.TEXT,anchor='mm')
        d.line((12,46,228,46),fill=theme.LINE)
        d.text((14,58),'Current: '+str(self.data.get('installed') or '...'),font=self.small,fill=theme.MUTED)
        d.text((14,77),'Latest: '+str(self.data.get('available') or 'Check first'),font=self.small,fill=theme.MUTED)
        labels=['Cancel','Install now'] if self.confirm else ['Check for updates','Install update','Back']
        if self.confirm:
            d.text((14,103),'Restart screen to update?',font=self.small,fill=theme.TEXT)
        for i,label in enumerate(labels):
            y=132+32*i
            if i==self.index:
                d.rectangle((10,y-4,229,y+24),outline='white')
            d.text((22,y),label,font=self.font,fill=theme.TEXT)
        message='Working...' if self.pending else str(self.data.get('message') or '')
        # Measure pixels, including long tokens, inside a dedicated status area.
        lines=[];line=''
        for char in ' '.join(message.split()):
            if d.textlength(line+char,font=self.small)>212:
                lines.append(line.rstrip());line=char.lstrip()
            else:line+=char
        if line:lines.append(line)
        if len(lines)>3:
            lines=lines[:3]
            while lines[-1] and d.textlength(lines[-1]+'…',font=self.small)>212:
                lines[-1]=lines[-1][:-1]
            lines[-1]+='…'
        for i,line in enumerate(lines):
            d.text((14,226+14*i),line,font=self.small,fill=theme.ACCENT)
        d.line((12,273,228,273),fill=theme.LINE)
        theme.footer_icons(img,right='enter',enabled=not (self.pending or self.data.get('busy')))
        return img


class SystemInfoMenu:
    """Read-only, asynchronous diagnostics in three pages for the PiTFT."""
    def __init__(self):
        self.page=0;self.data={};self.pending=False;self.results=queue.Queue();self.last=0
        self.font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',15)
        self.small=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',12)
    def enter(self):
        self.page=0;self.refresh()
    def refresh(self):
        if self.pending:return
        self.pending=True;self.last=time.monotonic()
        def worker():
            import os,subprocess
            from pathlib import Path
            def read(path):
                try:return Path(path).read_text().strip().strip('\x00')
                except OSError:return ''
            data={}
            try:
                with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM) as s:
                    s.settimeout(5);s.connect('/run/pitalk-update/control.sock');s.sendall(b'{"action":"status"}\n')
                    with s.makefile('rb') as f:state=json.loads(f.readline(8192))
                data['version']=state.get('installed')
            except Exception:pass
            data['model']=read('/proc/device-tree/model') or None
            data['kernel']=os.uname().release;data['arch']=os.uname().machine
            for line in read('/etc/os-release').splitlines():
                if line.startswith('PRETTY_NAME='):data['os']=line.split('=',1)[1].strip('"')
            try:data['temp']=f"{float(read('/sys/class/thermal/thermal_zone0/temp'))/1000:.1f} °C"
            except ValueError:pass
            try:
                seconds=int(float(read('/proc/uptime').split()[0]));data['uptime']=f'{seconds//86400}d {seconds%86400//3600}h {seconds%3600//60}m'
            except (ValueError,IndexError):pass
            try:
                raw=subprocess.check_output(['/usr/bin/vcgencmd','get_throttled'],text=True,timeout=3)
                data['flags']=int(raw.split('=',1)[1],16)
            except Exception:pass
            self.results.put(data)
        threading.Thread(target=worker,daemon=True).start()
    def poll(self):
        changed=False
        try:self.data=self.results.get_nowait();self.pending=False;changed=True
        except queue.Empty:pass
        if time.monotonic()-self.last>10:self.refresh()
        return changed
    def button(self,name):
        if name=='BACK':return True
        if name in ('UP','DOWN'):self.page=(self.page+(1 if name=='DOWN' else -1))%3
        elif name=='ENTER':self.refresh()
        return False
    def render(self):
        img=Image.new('RGB',(240,320),theme.BG);d=theme.MenuDraw(img)
        d.text((144,29),'System Info',font=self.font,fill=theme.TEXT,anchor='mm')
        d.line((12,46,228,46),fill=theme.LINE)
        title=['Software','Hardware','Power status'][self.page]
        d.text((14,57),f'{title}  {self.page+1}/3',font=self.font,fill=theme.ACCENT)
        data=self.data;flags=data.get('flags')
        def flag(mask,yes,no):return None if flags is None else yes if flags&mask else no
        rows=[ [('PiTALK version',data.get('version')),('Operating system',data.get('os')),('Kernel',data.get('kernel')),('Architecture',data.get('arch'))],
               [('Model',data.get('model')),('Uptime',data.get('uptime')),('CPU temperature',data.get('temp'))],
               [('Undervoltage now',flag(1,'Detected','Not detected')),('Throttling now',flag(4,'Active','Inactive')),('Undervoltage since boot',flag(65536,'Recorded','Not recorded')),('Throttling since boot',flag(262144,'Recorded','Not recorded'))] ][self.page]
        for i,(label,value) in enumerate(rows):
            y=88+i*42
            d.text((14,y),label,font=self.small,fill=theme.MUTED)
            d.text((14,y+16),value or 'Unavailable',font=self.small,fill=theme.TEXT)
        d.line((12,273,228,273),fill=theme.LINE)
        theme.footer_icons(img,right='enter',enabled=not self.pending)
        d.text((60,284),'Reading…' if self.pending else 'Enter: refresh',font=self.small,fill=theme.MUTED)
        d.text((60,301),'Up / Down: pages',font=self.small,fill=theme.MUTED)
        return img
