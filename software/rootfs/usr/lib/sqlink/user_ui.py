"""Shared reflector profiles, operated with the four PiTFT buttons."""
import copy,queue,threading
from PIL import Image,ImageDraw
from .wifi_ui import WiFiMenu,request
from . import theme

class UserMenu(WiFiMenu):
 fields=[('name','Profile name'),('host','Server hostname'),('port','Server port'),('login','Callsign / Login'),('password','Password'),('default_tg','Default TG'),('monitored','Monitored TGs'),('timeout','Monitor timeout'),('directory','Station directory')]
 def __init__(self):
  super().__init__();self.data={'profiles':[]};self.draft={};self.buffer='';self.profile_id=None;self.dirty=False;self.return_page='list';self.page='list';self.epoch=0
 def cancel(self):
  self.epoch+=1;self.buffer='';self.draft={};self.page='list';self.dirty=False
 def enter(self):
  self.cancel();self.index=0;self.send({'action':'profiles_snapshot'},'list')
 def send(self,payload,target):
  if self.busy:return
  self.busy=True;epoch=self.epoch
  def worker():
   try:r=request(payload)
   except Exception:r={'ok':False,'message':'Profile service unavailable.'}
   finally:
    if isinstance(payload.get('settings'),dict):payload['settings'].pop('password',None)
   self.results.put((epoch,target,r))
  threading.Thread(target=worker,daemon=True).start()
 def poll(self):
  try:epoch,target,r=self.results.get_nowait()
  except queue.Empty:return False
  self.busy=False
  if epoch!=self.epoch:return False
  self.message=r.get('message','')
  if r.get('ok'):
   self.data=r;self.page=target;self.index=0;self.buffer='';self.draft={};self.dirty=False
  else:self.return_page='form' if self.draft else 'list';self.page='error'
  return True
 def profile(self):return next((p for p in self.data['profiles'] if p['id']==self.profile_id),{})
 def payload(self,action):return dict(action=action,id=self.profile_id,revision=self.data.get('revision'),confirm=True)
 def rows(self):
  if self.page=='list':
   return [(p['name'],('Active ' if p['id']==self.data.get('active') else '')+('Default ' if p['id']==self.data.get('default') else '')+('Incomplete' if not p['ready'] else p['host'])) for p in self.data['profiles']]+[('Add profile','Create another connection')]
  if self.page=='detail':return [('Edit profile','Settings and credentials'),('Activate','Reconnect to this server'),('Set as default','Use at next boot'),('Delete profile','Active/default protected')]
  if self.page=='form':
   rows=[]
   for k,label in self.fields:
    v=self.draft.get(k,'')
    if k=='password':v='New password set' if v else 'Configured' if self.draft.get('password_set') else 'Not set'
    if k=='directory':v='SQLink API' if v=='sqlink' else 'Local TG numbers only'
    rows.append((label,str(v) or 'Not set'))
   return rows+[('Save profile','Does not switch connection')]
  return []
 def button(self,name):
  if self.busy:return False
  if self.page=='error':
   if name in ('BACK','ENTER'):self.page=self.return_page;self.index=0
   return False
  if self.page=='keyboard':
   if name=='BACK':self.buffer='';self.page='form';return False
   keys=self.keys()
   if name in ('UP','DOWN'):self.key_index=(self.key_index+(1 if name=='DOWN' else -1))%len(keys)
   elif name=='ENTER':
    k=keys[self.key_index]
    if k in ('abc','ABC','123','#+='):self.charset=k;self.key_index=0
    elif k=='DEL':self.buffer=self.buffer[:-1]
    elif k=='OK':
     if self.edit_key!='password' or self.buffer:self.draft[self.edit_key]=self.buffer;self.dirty=True
     self.buffer='';self.page='form'
    elif len(self.buffer)<(512 if self.edit_key=='monitored' else 253 if self.edit_key=='host' else 128):self.buffer+=' ' if k=='SP' else k
   return False
  if self.page=='confirm':
   if name=='BACK':self.page=self.confirm_return;self.index=0
   elif name in ('UP','DOWN'):self.index=1-self.index
   elif name=='ENTER':
    if self.index==0:self.page=self.confirm_return;self.index=0
    elif self.pending=='discard':self.draft={};self.dirty=False;self.page='list';self.index=0
    else:self.send(self.payload(self.pending),'list')
   return False
  if name=='BACK':
   if self.page=='list':self.cancel();return True
   if self.page=='form' and self.dirty:self.confirm('discard','Discard changes?','form');return False
   self.page='list';self.index=0;self.draft={};return False
  rows=self.rows()
  if name in ('UP','DOWN'):self.index=(self.index+(1 if name=='DOWN' else -1))%max(1,len(rows))
  elif name=='ENTER':
   if self.page=='list':
    if self.index==len(self.data['profiles']):
     self.profile_id=None;self.draft=dict(name='New profile',host='',port='',login='',default_tg='0',monitored='',timeout='30',directory='none');self.page='form';self.dirty=True
    else:self.profile_id=self.data['profiles'][self.index]['id'];self.page='detail'
    self.index=0
   elif self.page=='detail':
    if self.index==0:self.draft=copy.deepcopy(self.profile());self.page='form';self.index=0;self.dirty=False
    else:
     action,label=[('', ''),('profiles_activate','Activate and reconnect?'),('profiles_default','Use at next boot?'),('profiles_delete','Delete this profile?')][self.index]
     self.confirm(action,label,'detail')
   elif self.page=='form':
    if self.index==len(self.fields):
     payload=self.payload('profiles_save');payload['settings']=dict(self.draft);self.send(payload,'list')
    else:
     self.edit_key=self.fields[self.index][0]
     if self.edit_key=='directory':self.draft['directory']='none' if self.draft.get('directory')=='sqlink' else 'sqlink';self.dirty=True
     else:self.buffer='' if self.edit_key=='password' else str(self.draft.get(self.edit_key,''));self.charset='123' if self.edit_key in ('port','default_tg','timeout','monitored') else 'abc';self.key_index=0;self.page='keyboard'
  return False
 def confirm(self,action,label,back):self.pending=action;self.confirm_label=label;self.confirm_return=back;self.page='confirm';self.index=0
 def render(self):
  img=Image.new('RGB',(240,320),theme.BG);d=ImageDraw.Draw(img)
  d.text((144,29),'Profiles',font=self.title,fill=theme.TEXT,anchor='mm');d.line((12,46,228,46),fill=theme.LINE)
  def text(x,y,value,font=None,color=None,width=208):
   font=font or self.font;value=str(value)
   while value and d.textlength(value,font=font)>width:value=value[:-1]
   d.text((x,y),value,font=font,fill=color or theme.TEXT)
  def row(y,label,sub,selected):
   if selected:d.rounded_rectangle((10,y-3,229,y+35),radius=5,fill=theme.SELECTED)
   text(18,y,label);text(18,y+19,sub,self.small,theme.MUTED)
  if self.busy:text(16,90,'Please wait...');text(16,125,'Reading / applying profile',self.small)
  elif self.page=='keyboard':
   text(12,59,dict(self.fields)[self.edit_key]);text(12,84,'*'*min(len(self.buffer),24) if self.edit_key=='password' else self.buffer[-27:],self.small)
   keys=self.keys();start=max(0,self.key_index//6-4)
   for i in range(start*6,min(len(keys),(start+5)*6)):
    x=9+i%6*37;y=109+(i//6-start)*28
    if i==self.key_index:d.rounded_rectangle((x,y,x+35,y+25),radius=4,fill=theme.SELECTED,outline=theme.ACCENT)
    text(x+3,y+4,keys[i],self.small,width=31)
   text(12,253,'OK keeps draft; BACK cancels',self.small)
  elif self.page=='confirm':
   text(12,70,self.confirm_label);text(12,98,self.profile().get('name',''),self.small)
   row(142,'Cancel','',self.index==0);row(195,'Confirm','',self.index==1)
  elif self.page=='error':
   line='';y=70
   for word in self.message.split():
    if d.textlength((line+' '+word).strip(),font=self.font)>208:text(12,y,line);line=word;y+=24
    else:line=(line+' '+word).strip()
   text(12,y,line)
  else:
   label=('Active: '+self.data.get('active_name','')) if self.page=='list' else self.profile().get('name','New profile')
   text(12,57,label,self.small,theme.ACCENT)
   rows=self.rows();start=max(0,self.index-3)
   for i in range(start,min(len(rows),start+4)):row(86+(i-start)*43,*rows[i],self.index==i)
  d.line((12,273,228,273),fill=theme.LINE);theme.footer_icons(img,right='enter',enabled=not self.busy)
  return img
