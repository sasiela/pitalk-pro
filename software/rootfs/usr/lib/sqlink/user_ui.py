"""User settings draft with explicit save, masked password and four-button keyboard."""
import threading,queue
from PIL import Image,ImageDraw
from .wifi_ui import WiFiMenu,request
from . import theme

class UserMenu(WiFiMenu):
    fields=[('login','Callsign / Login'),('password','Password'),('default_tg','Default TG'),('monitored','Monitored TGs'),('timeout','Monitor timeout')]
    def __init__(self):
        super().__init__();self.draft={};self.revision='';self.buffer='';self.edit_key='';self.dirty=False
    def cancel(self):
        self.buffer='';self.draft.pop('password',None);self.dirty=False;self.page='home'
    def enter(self):
        self.cancel();self.index=0;self.start_user({'action':'user_snapshot'})
    def start_user(self,payload):
        if self.busy:return
        self.busy=True
        def worker():
            try:r=request(payload)
            except Exception:r={'ok':False,'message':'Settings service unavailable.'}
            finally:
                if isinstance(payload.get('settings'),dict):payload['settings'].pop('password',None)
            self.results.put(r)
        threading.Thread(target=worker,daemon=True).start()
    def poll(self):
        try:r=self.results.get_nowait()
        except queue.Empty:return False
        self.busy=False;self.buffer='';self.draft.pop('password',None)
        if r.get('ok'):
            self.draft=r['settings'];self.revision=self.draft.pop('revision');self.page='home';self.index=0;self.dirty=False
        else:self.page='error'
        self.message=r.get('message','');return True
    def button(self,name):
        if self.busy:return False
        if self.page=='edit':
            if name=='BACK':self.buffer='';self.page='home';return False
            keys=self.keys()
            if name in ('UP','DOWN'):self.key_index=(self.key_index+(1 if name=='DOWN' else -1))%len(keys)
            elif name=='ENTER':
                k=keys[self.key_index]
                if k in ('abc','ABC','123','#+='):self.charset=k;self.key_index=0
                elif k=='DEL':self.buffer=self.buffer[:-1]
                elif k=='OK':
                    if self.edit_key!='password' or self.buffer:
                        self.draft[self.edit_key]=self.buffer;self.dirty=True
                    self.buffer='';self.page='home'
                elif len(self.buffer)<(512 if self.edit_key=='monitored' else 128):self.buffer+=' ' if k=='SP' else k
            return False
        if self.page in ('confirm','discard'):
            if name=='BACK':self.page='home';return False
            if name in ('UP','DOWN'):self.index=1-self.index
            if name=='ENTER':
                if self.index==0:self.page='home';self.index=0
                elif self.page=='discard':self.cancel();return True
                else:self.start_user({'action':'user_save','confirm':True,'settings':dict(self.draft),'revision':self.revision})
            return False
        if self.page=='error':
            if name in ('BACK','ENTER'):self.page='home';self.index=0
            return False
        if name=='BACK':
            if self.dirty:self.page='discard';self.index=0;return False
            self.cancel();return True
        if name in ('UP','DOWN'):self.index=(self.index+(1 if name=='DOWN' else -1))%6
        elif name=='ENTER':
            if self.index==5:self.page='confirm';self.index=0
            else:
                self.edit_key=self.fields[self.index][0];self.buffer='' if self.edit_key=='password' else str(self.draft.get(self.edit_key,''));self.charset='ABC' if self.edit_key=='login' else 'abc' if self.edit_key=='password' else '123';self.key_index=0;self.page='edit'
        return False
    def render(self):
        img=Image.new('RGB',(240,320),theme.BG);d=ImageDraw.Draw(img)
        d.text((144,29),'User',font=self.title,fill=theme.TEXT,anchor='mm');d.line((12,46,228,46),fill=theme.LINE)
        def text(x,y,t,font=None,color=None,width=208):
            font=font or self.font;t=str(t)
            while t and d.textlength(t,font=font)>width:t=t[:-1]
            d.text((x,y),t,font=font,fill=color or theme.TEXT)
        def row(y,label,selected,sub=''):
            if selected:d.rounded_rectangle((10,y-3,229,y+35),radius=5,fill=theme.SELECTED)
            text(18,y,label)
            if sub:text(18,y+19,sub,self.small,theme.MUTED)
        if self.busy:text(16,90,'Please wait...');text(16,125,'Saving / reconnecting' if self.page=='confirm' else 'Reading settings',self.small)
        elif self.page=='edit':
            label=dict(self.fields)[self.edit_key];text(12,59,label)
            text(12,84,'*'*min(len(self.buffer),24) if self.edit_key=='password' else self.buffer[-27:],self.small)
            keys=self.keys();start=max(0,self.key_index//6-4)
            for i in range(start*6,min(len(keys),(start+5)*6)):
                x=9+i%6*37;y=109+(i//6-start)*28
                if i==self.key_index:d.rounded_rectangle((x,y,x+35,y+25),radius=4,fill=theme.SELECTED,outline=theme.ACCENT)
                text(x+3,y+4,keys[i],self.small,width=31)
            text(12,253,'OK keeps draft; BACK cancels',self.small)
        elif self.page in ('confirm','discard'):
            text(12,70,'Reconnect with changes?' if self.page=='confirm' else 'Discard unsaved changes?')
            row(132,'Cancel',self.index==0);row(183,'Save & reconnect' if self.page=='confirm' else 'Discard',self.index==1)
        elif self.page=='error':
            words=self.message.split();line='';y=70
            for word in words:
                if d.textlength((line+' '+word).strip(),font=self.font)>208:text(12,y,line);line=word;y+=24
                else:line=(line+' '+word).strip()
            text(12,y,line)
        else:
            text(12,57,'Unsaved changes' if self.dirty else self.message or 'Reflector account',self.small,theme.ACCENT)
            start=max(0,self.index-3)
            for i in range(start,min(6,start+4)):
                if i==5:label='Save & reconnect';value='Apply all changes'
                else:
                    k,label=self.fields[i];value=('New password set' if 'password' in self.draft else 'Configured' if self.draft.get('password_set') else 'Not set') if k=='password' else str(self.draft.get(k,''))
                    if k=='timeout':value+=' seconds'
                row(86+(i-start)*43,label,self.index==i,value)
        d.line((12,273,228,273),fill=theme.LINE);theme.footer_icons(img,right='enter',enabled=not self.busy)
        return img
