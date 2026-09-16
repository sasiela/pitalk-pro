"""Bluetooth device and audio management for the PiTFT."""
import json,socket,threading,queue,time
from PIL import Image,ImageDraw,ImageFont
from . import theme


def request(payload):
    with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM) as sock:
        sock.settimeout(110);sock.connect('/run/sqlink-bluetooth/control.sock')
        sock.sendall((json.dumps(payload)+'\n').encode())
        with sock.makefile('rb') as f:data=f.readline(262145)
    if len(data)>262144:raise ValueError()
    return json.loads(data)


class BluetoothMenu:
    def __init__(self):
        self.page='home';self.index=0;self.status={};self.selected=None
        self.busy=False;self.operation='';self.message='';self.challenge=None;self.pin='';self.key=0
        self.results=queue.Queue();self.last_poll=0;self.polling=False;self.target='home'
        self.font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',15)
        self.small=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',12)
        self.title=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',20)
    def send(self,payload,target=None,aux=False):
        if not aux:
            if self.busy:return
            self.busy=True;self.operation=payload['action'];self.target=target or self.page
            self.message={'scan':'Scanning for 10 seconds...','pair':'Put device in pairing mode...','connect':'Connecting...'}.get(self.operation,'Please wait...')
        def worker():
            try:r=request(payload)
            except Exception:r=dict(ok=False,message='Bluetooth service unavailable.')
            self.results.put(('aux' if aux else 'done',r))
        threading.Thread(target=worker,daemon=True).start()
    def enter(self):
        self.page='home';self.index=0;self.send({'action':'status'},'home')
    def cancel(self):
        if self.busy and self.operation=='pair':self.send({'action':'cancel_pair'},aux=True)
        self.pin='';self.challenge=None
    def poll(self):
        if self.busy and self.operation=='pair' and not self.polling and time.monotonic()-self.last_poll>0.7:
            self.polling=True;self.last_poll=time.monotonic()
            def poller():
                try:r=request({'action':'challenge'})
                except Exception:r={}
                self.results.put(('challenge',r))
            threading.Thread(target=poller,daemon=True).start()
        changed=False
        while True:
            try:kind,r=self.results.get_nowait()
            except queue.Empty:break
            if kind=='challenge':
                self.polling=False
                new=r.get('challenge') if self.busy and self.operation=='pair' else None
                if new!=self.challenge:
                    self.challenge=new;self.index=0;self.pin='';self.key=0;changed=True
            elif kind=='done':
                self.busy=False;self.challenge=None;self.pin='';self.message=r.get('message','')
                if r.get('ok'):
                    self.status=r.get('status',self.status);self.page=self.target;self.index=0
                    if self.selected:
                        self.selected=next((d for d in self.status.get('devices',[]) if d['mac']==self.selected['mac']),self.selected)
                else:self.page='error';self.index=0
                changed=True
            elif not r.get('ok'):
                self.message=r.get('message','Request failed.');changed=True
        return changed
    def items(self):
        if self.page=='home':return ['Scan devices','Saved devices','Audio routing','Refresh status','Power off' if self.status.get('powered') else 'Power on']
        if self.page in ('scan','saved'):
            return [d for d in self.status.get('devices',[]) if self.page=='scan' or d['paired']]
        if self.page=='device':
            d=self.selected
            if not d['paired']:return ['Pair device','Back']
            return ['Disconnect' if d['connected'] else 'Connect','Audio profiles','Auto-connect: '+('On' if d['auto'] else 'Off'),'Forget device','Back']
        if self.page=='audio':return ['Output device','Input microphone','Bluetooth profiles']
        if self.page in ('sinks','sources'):return self.status.get('audio',{}).get(self.page,[])
        if self.page=='profiles':
            cards=self.status.get('audio',{}).get('cards',[])
            if self.selected and self.target=='profiles' and self.selected.get('mac'):
                mac=self.selected['mac'].replace(':','_');cards=[c for c in cards if mac in c['name']]
            return [dict(p,card=c['name'],active=p['name']==c['active']) for c in cards for p in c['profiles']]
        if self.page in ('forget','poweroff'):return ['Cancel','Forget device' if self.page=='forget' else 'Power off']
        return []
    def button(self,name):
        if self.busy:
            c=self.challenge
            if name=='BACK':self.cancel();return False
            if not c:return False
            if c['kind'] in ('pin','passkey'):
                keys=list('0123456789')+['DEL','OK']
                if name in ('UP','DOWN'):self.key=(self.key+(1 if name=='DOWN' else -1))%len(keys)
                elif name=='ENTER':
                    value=keys[self.key]
                    if value=='DEL':self.pin=self.pin[:-1]
                    elif value=='OK' and self.pin:
                        self.send({'action':'answer','id':c['id'],'accept':True,'value':self.pin},aux=True);self.challenge=None;self.pin=''
                    elif value.isdigit() and len(self.pin)<(6 if c['kind']=='passkey' else 16):self.pin+=value
            elif c['kind']=='confirm':
                if name in ('UP','DOWN'):self.index=1-self.index
                elif name=='ENTER':self.send({'action':'answer','id':c['id'],'accept':self.index==1},aux=True);self.challenge=None
            return False
        if name=='BACK':
            if self.page=='home':return True
            self.page='home';self.index=0;self.selected=None;self.message='';return False
        if self.page=='error':
            if name=='ENTER':self.enter()
            return False
        items=self.items()
        if name in ('UP','DOWN') and items:self.index=(self.index+(1 if name=='DOWN' else -1))%len(items)
        if name!='ENTER' or not items:return False
        item=items[self.index]
        if self.page=='home':
            if self.index==0:self.send({'action':'scan'},'scan')
            elif self.index==1:self.send({'action':'status'},'saved')
            elif self.index==2:self.selected=None;self.send({'action':'status'},'audio')
            elif self.index==3:self.send({'action':'status'},'home')
            elif self.status.get('powered'):self.page='poweroff';self.index=0
            else:self.send({'action':'power','on':True},'home')
        elif self.page in ('scan','saved'):self.selected=item;self.page='device';self.index=0
        elif self.page=='device':
            d=self.selected;mac=d['mac']
            if item=='Back':self.page='home';self.index=0
            elif item=='Pair device':self.send({'action':'pair','mac':mac},'device')
            elif item in ('Connect','Disconnect'):self.send({'action':item.lower(),'mac':mac},'device')
            elif item=='Audio profiles':self.send({'action':'status'},'profiles')
            elif item.startswith('Auto-connect'):self.send({'action':'auto','mac':mac,'on':not d['auto']},'device')
            elif item=='Forget device':self.page='forget';self.index=0
        elif self.page=='audio':self.page=['sinks','sources','profiles'][self.index];self.index=0
        elif self.page in ('sinks','sources'):self.send({'action':'route','kind':'sink' if self.page=='sinks' else 'source','name':item['name']},'audio')
        elif self.page=='profiles':self.send({'action':'profile','card':item['card'],'profile':item['name']},'audio')
        elif self.page in ('forget','poweroff'):
            if self.index==0:self.page='home';self.index=0
            elif self.page=='forget':self.send({'action':'forget','mac':self.selected['mac'],'confirm':True},'saved')
            else:self.send({'action':'power','on':False},'home')
        return False
    def render(self):
        img=Image.new('RGB',(240,320),theme.BG);d=ImageDraw.Draw(img)
        def text(x,y,value,font=None,color=None,width=208):
            font=font or self.font;value=''.join(c if c.isprintable() else '?' for c in str(value))
            if d.textlength(value,font=font)>width:
                while value and d.textlength(value+'…',font=font)>width:value=value[:-1]
                value+='…'
            d.text((x,y),value,font=font,fill=color or theme.TEXT)
        def row(y,label,selected,sub=''):
            if selected:
                d.rounded_rectangle((10,y-3,229,y+32),radius=5,fill=theme.SELECTED)
                d.rounded_rectangle((10,y,13,y+28),radius=1,fill=theme.ACCENT)
            text(22,y,label,width=196)
            if sub:text(22,y+19,sub,self.small,theme.MUTED,width=196)
        d.text((144,29),'Bluetooth',font=self.title,fill=theme.TEXT,anchor='mm');d.line((12,46,228,46),fill=theme.LINE)
        if self.busy:
            c=self.challenge
            text(12,61,self.selected['name'] if self.selected else 'Bluetooth')
            if c:
                text(12,91,'Confirm code' if c['kind']=='confirm' else 'Pairing code',self.small,theme.MUTED)
                text(12,116,c.get('code') or ('*'*len(self.pin)),self.title,theme.ACCENT)
                if c['kind']=='confirm':row(166,'Reject',self.index==0);row(210,'Confirm',self.index==1)
                elif c['kind'] in ('pin','passkey'):
                    for i,k in enumerate(list('0123456789')+['DEL','OK']):
                        x=12+i%4*55;y=153+i//4*33
                        if i==self.key:d.rounded_rectangle((x,y,x+49,y+28),radius=4,fill=theme.SELECTED,outline=theme.ACCENT)
                        text(x+10,y+5,k,self.small,width=36)
                else:text(12,160,'Enter code on other device.',self.small)
            else:
                text(12,108,self.message,self.small);text(12,140,'Keep the device nearby.',self.small,theme.MUTED)
                if self.operation=='pair':text(12,180,'Back cancels pairing.',self.small,theme.MUTED)
        elif self.page=='error':
            words=self.message.split();line='';y=80
            for word in words:
                if d.textlength((line+' '+word).strip(),font=self.font)>208:text(12,y,line);y+=25;line=word
                else:line=(line+' '+word).strip()
            text(12,y,line);text(12,225,'Check device / pairing mode.',self.small,theme.MUTED)
        else:
            top=93;visible=4;items=self.items()
            titles={'scan':'Nearby devices','saved':'Saved devices','audio':'Audio routing','sinks':'Output device','sources':'Input microphone','profiles':'Audio profiles','forget':'Forget this device?','poweroff':'Turn Bluetooth off?'}
            if self.page=='home':
                text(12,58,'Bluetooth '+('On' if self.status.get('powered') else 'Off'),self.font,theme.ACCENT)
                count=sum(bool(x['connected']) for x in self.status.get('devices',[]));text(12,80,f'{count} connected',self.small,theme.MUTED)
                top=108;visible=5
            elif self.page=='device':text(12,58,self.selected['name']);text(12,79,self.selected['mac'],self.small,theme.MUTED);top=106
            else:text(12,61,titles.get(self.page,self.page))
            if not items:text(12,125,'No devices available.',self.font);text(12,152,'Connect or scan again.',self.small,theme.MUTED)
            start=max(0,self.index-visible+1)
            for i in range(start,min(len(items),start+visible)):
                item=items[i];sub='';label=item
                if isinstance(item,dict):
                    label=item.get('label',item['name'])
                    if self.page in ('scan','saved'):sub=('Connected' if item['connected'] else 'Paired' if item['paired'] else 'Not paired')+'  '+item['mac'][-5:]
                    elif self.page in ('sinks','sources'):
                        kind='sink' if self.page=='sinks' else 'source';sub='Selected' if item['name']==self.status.get('audio',{}).get(kind) else ''
                    elif self.page=='profiles':sub='Selected' if item['active'] else ''
                row(top+(i-start)*(31 if self.page=='home' else 39),label,i==self.index,sub)
            if self.page=='profiles' and not items:text(12,190,'Connect a headset first.',self.small,theme.MUTED)
        d.line((12,273,228,273),fill=theme.LINE);theme.footer_icons(img,right='enter',enabled=not self.busy or self.operation=='pair')
        return img
