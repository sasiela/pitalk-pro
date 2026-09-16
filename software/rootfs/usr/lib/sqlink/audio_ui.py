"""Combined microphone and speaker selection for SQLink."""
from PIL import Image,ImageDraw
from .bluetooth_ui import BluetoothMenu, request
import threading, queue
from . import theme

class AudioMenu(BluetoothMenu):
    def __init__(self):
        super().__init__()
        self.volume_pending=None
        self.volume_running=False
        self.volume_results=queue.Queue()

    def flush_volume(self):
        if self.volume_running or self.volume_pending is None:return
        payload=self.volume_pending;self.volume_pending=None;self.volume_running=True
        def worker():
            try:result=request(payload)
            except Exception:result={'ok':False,'message':'Could not set volume. Try again.'}
            self.volume_results.put(result)
        threading.Thread(target=worker,daemon=True).start()

    def poll(self):
        changed=super().poll()
        try:result=self.volume_results.get_nowait()
        except queue.Empty:return changed
        self.volume_running=False
        if not result.get('ok'):
            self.volume_pending=None
            self.message=result.get('message','Could not set volume.')
            self.page='error'
        elif self.volume_pending is None:
            self.status=result.get('status',self.status)
        self.flush_volume()
        return True

    def button(self,name):
        if self.busy:return False
        if self.page=='volume':
            if name in ('BACK','ENTER'):
                self.page='home';self.index=2
            elif name in ('UP','DOWN'):
                a=self.status.get('audio',{});sink=next((x for x in a.get('sinks',[]) if x['name']==a.get('sink')),None)
                if sink:
                    value=max(0,min(100,sink.get('volume',0)+(5 if name=='UP' else -5)))
                    sink['volume']=value
                    self.volume_pending={'action':'volume','sink':sink['name'],'value':value}
                    self.flush_volume()
            return False
        if name=='BACK':
            if self.page=='error':self.enter();return False
            return True
        if self.page=='error':
            if name=='ENTER':self.enter()
            return False
        if name in ('UP','DOWN'):self.index=(self.index+(1 if name=='DOWN' else -1))%4
        elif name=='ENTER':
            if self.volume_running:return False
            if self.index==2:self.send({'action':'status'},'volume')
            elif self.index==3:self.enter()
            else:self.send({'action':'transport','transport':('usb','bluetooth')[self.index]},'home')
        return False

    def render(self):
        img=Image.new('RGB',(240,320),theme.BG);d=ImageDraw.Draw(img)
        d.text((144,29),'Volume' if self.page=='volume' else 'Audio',font=self.title,fill=theme.TEXT,anchor='mm')
        d.line((12,46,228,46),fill=theme.LINE)
        def text(y,t,font=None,color=None):d.text((16,y),t,font=font or self.font,fill=color or theme.TEXT)
        def wrapped(y,t):
            line=''
            for word in t.split():
                test=(line+' '+word).strip()
                if d.textlength(test,font=self.font)>206:
                    text(y,line);y+=23;line=word
                else:line=test
            text(y,line)
        if self.busy:text(83,'Switching audio...' if self.operation=='transport' else 'Reading audio...')
        elif self.page=='error':wrapped(66,self.message)
        elif self.page=='volume':
            a=self.status.get('audio',{});device=next((x for x in a.get('sinks',[]) if x['name']==a.get('sink')),None)
            if not device:text(85,'No audio output')
            else:
                text(65,'Bluetooth' if device['name'].startswith('bluez_') else 'USB audio' if '.usb-' in device['name'] else 'Audio output',color=theme.ACCENT)
                value=device.get('volume',0)
                d.text((120,130),str(value)+'%',font=self.title,fill=theme.TEXT,anchor='mm')
                d.rounded_rectangle((20,166,220,182),radius=6,fill=theme.PANEL)
                if value:d.rounded_rectangle((20,166,20+2*min(value,100),182),radius=6,fill=theme.ACCENT)
                text(205,'UP +5% / DOWN -5%',self.small)
                text(231,'Muted' if device.get('mute') else 'Changes apply immediately',self.small,theme.MUTED)
        else:
            a=self.status.get('audio',{});sink=a.get('sink','');source=a.get('source','')
            usb=sink.startswith('alsa_output.usb-') and source.startswith('alsa_input.usb-')
            bt=sink.startswith('bluez_output.') and source.startswith('bluez_input.')
            text(61,'Active: '+('USB audio' if usb else 'Bluetooth' if bt else 'Other / mixed'),color=theme.ACCENT)
            text(87,'Microphone + speaker',self.small,theme.MUTED)
            for i,label in enumerate(['USB audio card','Bluetooth headset','Volume','Refresh status']):
                y=111+i*36
                if i==self.index:
                    d.rounded_rectangle((10,y-5,229,y+31),radius=5,fill=theme.SELECTED)
                    d.rounded_rectangle((10,y-2,13,y+28),radius=1,fill=theme.ACCENT)
                selected=(i==0 and usb) or (i==1 and bt)
                text(y,('✓ ' if selected else '')+label)
            text(253,'Pair devices in Bluetooth menu',self.small,theme.MUTED)
        d.line((12,273,228,273),fill=theme.LINE)
        theme.footer_icons(img,right='enter',enabled=not self.busy)
        return img
