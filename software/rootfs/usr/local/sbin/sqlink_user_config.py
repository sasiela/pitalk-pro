"""Restricted configuration editor. Never returns authentication secrets."""
import configparser,hashlib,pathlib,re,os,subprocess,time,datetime
CONFIG=pathlib.Path('/etc/svxlink/svxlink.conf')
def parse(text):
 c=configparser.ConfigParser(interpolation=None,strict=True);c.read_string(text);return c

def snapshot():
 raw=CONFIG.read_bytes();c=parse(raw.decode());s=c['ReflectorLogic']
 return dict(login=s.get('callsign','').strip('"'),password_set=bool(s.get('auth_key','')),default_tg=s.get('default_tg','0'),monitored=s.get('monitor_tgs',''),timeout=s.get('tg_select_timeout','30'),revision=hashlib.sha256(raw).hexdigest())

def validate(v):
 if not isinstance(v,dict):raise ValueError('Invalid settings.')
 login=v.get('login','').strip()
 if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9/_-]{0,31}',login):raise ValueError('Invalid callsign / login.')
 for key,lo,hi in [('default_tg',0,4294967295),('timeout',1,86400)]:
  value=str(v.get(key,''))
  if not re.fullmatch(r'[0-9]+',value) or not lo<=int(value)<=hi:raise ValueError('Invalid '+key.replace('_',' ')+'.')
 monitored=str(v.get('monitored','')).replace(' ','')
 if len(monitored)>512 or (monitored and any(not re.fullmatch(r'[1-9][0-9]{0,9}\+{0,3}',x) or int(x.rstrip('+'))>4294967295 for x in monitored.split(','))):raise ValueError('Use TG numbers separated by commas.')
 password=v.get('password')
 if password is not None and (not isinstance(password,str) or not 1<=len(password)<=128 or any(ord(x)<33 or ord(x)>126 or x in '\\"' for x in password)):raise ValueError('Password: 1-128 characters; no spaces, quotes or backslashes.')
 return login,monitored,password

def write_atomic(raw,mode,uid,gid):
 tmp=CONFIG.with_suffix('.user-tmp');tmp.write_bytes(raw);os.chmod(tmp,mode);os.chown(tmp,uid,gid);os.replace(tmp,CONFIG)

def dispatch(req):
 if req.get('action')=='user_snapshot':return dict(ok=True,settings=snapshot())
 try:
  if req.get('confirm') is not True:raise ValueError('Confirm Save & reconnect first.')
  v=req.get('settings');login,monitored,password=validate(v)
  old=CONFIG.read_bytes();st=CONFIG.stat()
  if req.get('revision')!=hashlib.sha256(old).hexdigest():raise ValueError('Settings changed. Reopen User and try again.')
  if pathlib.Path('/sys/class/gpio/gpio536/value').read_text().strip()!='1':raise ValueError('Release PTT before saving.')
  edits={'SimplexLogic':{'CALLSIGN':login},'ReflectorLogic':{'CALLSIGN':login,'DEFAULT_TG':str(int(v['default_tg'])),'MONITOR_TGS':monitored,'TG_SELECT_TIMEOUT':str(int(v['timeout']))}}
  if password is not None:edits['ReflectorLogic']['AUTH_KEY']='"'+password+'"'
  lines=[];section='';done=set()
  for line in old.decode().splitlines(keepends=True):
   m=re.match(r'\s*\[([^]]+)\]',line)
   if m:section=m[1]
   m=re.match(r'\s*([A-Z_]+)\s*=',line)
   if m and m[1] in edits.get(section,{}):
    key=m[1];line=key+'='+edits[section][key]+'\n';done.add((section,key))
   lines.append(line)
  if done!={(s,k) for s,d in edits.items() for k in d}:raise ValueError('Configuration fields missing.')
  raw=''.join(lines).encode();parse(raw.decode())
  backup=pathlib.Path('/var/backups/sqlink-user');backup.mkdir(mode=0o700,exist_ok=True);backup.chmod(0o700)
  b=backup/(datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f')+'.conf');b.write_bytes(old);b.chmod(0o600)
  log=pathlib.Path('/var/log/svxlink');offset=log.stat().st_size
  write_atomic(raw,st.st_mode&0o777,st.st_uid,st.st_gid)
  success=False
  try:
   subprocess.run(['systemctl','restart','svxlink.service'],check=True,timeout=20,capture_output=True)
   for _ in range(40):
    time.sleep(.5)
    with log.open('rb') as f:f.seek(offset);recent=f.read().decode(errors='ignore')
    if 'ReflectorLogic: Authentication OK' in recent and pathlib.Path('/dev/shm/sqlink_dtmf').is_symlink():success=True;break
   if not success:raise RuntimeError()
  except Exception:
   write_atomic(old,st.st_mode&0o777,st.st_uid,st.st_gid)
   subprocess.run(['systemctl','restart','svxlink.service'],timeout=20,capture_output=True)
   return dict(ok=False,message='Connection failed. Previous settings restored.')
  return dict(ok=True,settings=snapshot(),message='Saved and connected.')
 except ValueError as e:return dict(ok=False,message=str(e))
 except Exception:return dict(ok=False,message='Could not save settings. Check connection.')
