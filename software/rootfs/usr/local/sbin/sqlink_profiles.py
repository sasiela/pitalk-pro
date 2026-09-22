"""Root-owned reflector profiles. Public responses never contain passwords."""
import configparser,contextlib,copy,datetime,fcntl,hashlib,ipaddress,json,os,pathlib,re,subprocess,tempfile,time,uuid
BOOTING=False
BASE=pathlib.Path('/var/lib/sqlink-profiles')
PUBLIC=pathlib.Path('/var/lib/sqlink-profile-state/active.json')
CONFIG=pathlib.Path('/etc/svxlink/svxlink.conf')
BACKUPS=pathlib.Path('/var/backups/sqlink-profiles')
PTT=pathlib.Path('/sys/class/gpio/gpio536/value')
RADIO=pathlib.Path('/dev/shm/sqlink-radio-state')
PID=pathlib.Path('/run/svxlink.pid')
LOG=pathlib.Path('/var/log/svxlink')

def atomic(path,data,mode=0o600,owner=None):
 path.parent.mkdir(parents=True,exist_ok=True)
 fd,tmp=tempfile.mkstemp(prefix='.'+path.name,dir=path.parent)
 try:
  os.fchmod(fd,mode)
  if owner is not None:os.fchown(fd,*owner)
  with os.fdopen(fd,'wb') as f:f.write(data);f.flush();os.fsync(f.fileno())
  os.replace(tmp,path)
 finally:
  if os.path.exists(tmp):os.unlink(tmp)
def write_json(path,data,mode=0o600):atomic(path,json.dumps(data,ensure_ascii=True,sort_keys=True).encode(),mode)
def parse(raw):
 c=configparser.ConfigParser(interpolation=None);c.read_string(raw.decode());return c
def revision(db):return hashlib.sha256(json.dumps(db,sort_keys=True).encode()+CONFIG.read_bytes()).hexdigest()
def ready(p):return bool(p.get('host') and p.get('port') and p.get('login') and p.get('password'))
def publish(db):
 p=db['applied']
 PUBLIC.parent.mkdir(parents=True,exist_ok=True);PUBLIC.parent.chmod(0o755)
 write_json(PUBLIC,{k:p.get(k) for k in ('id','name','host','directory','default_tg','monitored')},0o644)
def save(db):write_json(BASE/'profiles.json',db)
def initialize():
 path=BASE/'profiles.json'
 if path.exists():return json.loads(path.read_text())
 s=parse(CONFIG.read_bytes())['ReflectorLogic']
 p=dict(id='sqlink',name='SQLink',host=s.get('hosts',s.get('host','')).strip('"'),port=s.get('host_port',''),login=s.get('callsign','').strip('"'),password=s.get('auth_key','').strip('"'),default_tg=s.get('default_tg','0'),monitored=s.get('monitor_tgs',''),timeout=s.get('tg_select_timeout','30'),directory='sqlink')
 fala=dict(id='fala',name='Fala',host='fala.zasieg.pl',port='',login='',password='',default_tg='0',monitored='',timeout='30',directory='none')
 db=dict(version=1,active='sqlink',default='sqlink',applied=copy.deepcopy(p),profiles=[p,fala]);save(db);publish(db);return db
@contextlib.contextmanager
def locked():
 BASE.mkdir(parents=True,exist_ok=True);BASE.chmod(0o700)
 with (BASE/'lock').open('a') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX)
  if recover() and not BOOTING and PID.exists():restart()
  yield initialize()
def recover():
 journal=BASE/'pending.json'
 if journal.exists():
  j=json.loads(journal.read_text());atomic(CONFIG,j['config'].encode(),j['mode'],(j['uid'],j['gid']));save(j['database']);publish(j['database']);journal.unlink();return True
def snapshot(db):
 rows=[]
 for p in db['profiles']:
  q={k:v for k,v in p.items() if k!='password'};q.update(password_set=bool(p.get('password')),ready=ready(p),pending=p['id']==db['active'] and p!=db['applied']);rows.append(q)
 return dict(profiles=rows,active=db['active'],default=db['default'],active_name=db['applied']['name'],revision=revision(db))
def validate(v,old=None):
 if not isinstance(v,dict):raise ValueError('Invalid profile.')
 p=copy.deepcopy(old or dict(id=uuid.uuid4().hex,password=''))
 for key,default in [('name',''),('host',''),('port',''),('login',''),('default_tg','0'),('monitored',''),('timeout','30'),('directory','none')]:
  value=v.get(key,default)
  if not isinstance(value,(str,int)):raise ValueError('Invalid '+key+'.')
  p[key]=str(value).strip()
 if not 1<=len(p['name'])<=32 or any(ord(c)<32 for c in p['name']):raise ValueError('Name: 1–32 printable characters.')
 host=p['host']
 try:ipaddress.ip_address(host)
 except ValueError:
  if not host or len(host)>253 or any(not re.fullmatch(r'[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?',part) for part in host.rstrip('.').split('.')):raise ValueError('Enter a server hostname or IP, without a URL or port.')
 for key,lo,hi in [('port',1,65535),('default_tg',0,4294967295),('timeout',1,86400)]:
  value=p[key]
  if key=='port' and not value:continue
  if not re.fullmatch(r'[0-9]+',value) or not lo<=int(value)<=hi:raise ValueError('Invalid '+key+'.')
  p[key]=str(int(value))
 if p['login'] and not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9/_-]{0,31}',p['login']):raise ValueError('Invalid callsign / login.')
 p['monitored']=p['monitored'].replace(' ','')
 if len(p['monitored'])>512 or (p['monitored'] and any(not re.fullmatch(r'[1-9][0-9]{0,9}\+{0,3}',x) or int(x.rstrip('+'))>4294967295 for x in p['monitored'].split(','))):raise ValueError('Use TG numbers separated by commas.')
 if p['directory'] not in ('sqlink','none'):raise ValueError('Unsupported station directory.')
 password=v.get('password')
 if password not in (None,''):
  if not isinstance(password,str) or not 1<=len(password)<=128 or any(ord(x)<33 or ord(x)>126 or x in '\\"' for x in password):raise ValueError('Password: no spaces, quotes or backslashes; maximum 128 characters.')
  p['password']=password
 return p

def render_config(raw,p):
 edits={'SimplexLogic':{'CALLSIGN':p['login']},'ReflectorLogic':{'HOSTS':p['host'],'HOST_PORT':p['port'],'CALLSIGN':p['login'],'AUTH_KEY':'"'+p['password']+'"','DEFAULT_TG':p['default_tg'],'MONITOR_TGS':p['monitored'],'TG_SELECT_TIMEOUT':p['timeout']}}
 lines=[];section=None;done=set()
 def missing():
  for key,val in edits.get(section,{}).items():
   if (section,key) not in done:lines.append(key+'='+val+'\n');done.add((section,key))
 for line in raw.decode().splitlines(keepends=True):
  m=re.match(r'\s*\[([^]]+)\]',line)
  if m:missing();section=m[1]
  m=re.match(r'\s*([A-Za-z_]+)\s*=',line)
  if m and m[1].upper() in edits.get(section,{}):
   key=m[1].upper();line=key+'='+edits[section][key]+'\n';done.add((section,key))
  # HOST is the older alternative; keep a single authoritative host field.
  if m and section=='ReflectorLogic' and m[1].upper()=='HOST':continue
  lines.append(line if line.endswith('\n') else line+'\n')
 missing();result=''.join(lines).encode();c=parse(result)
 if any(section not in c for section in edits):raise ValueError('Required SvxLink section is missing.')
 return result

def idle():
 if PTT.read_text().strip()!='1':raise ValueError('Release PTT before switching profiles.')
 parts=RADIO.read_text().split()
 if int(parts[0])!=int(PID.read_text()) or int(parts[2])!=0:raise ValueError('Wait until reception ends before switching profiles.')
def restart():subprocess.run(['systemctl','restart','svxlink.service'],check=True,timeout=20,capture_output=True)
def authenticated(offset,inode):
 deadline=time.monotonic()+20
 while time.monotonic()<deadline:
  time.sleep(.5)
  st=LOG.stat()
  with LOG.open('rb') as f:
   f.seek(offset if st.st_ino==inode and st.st_size>=offset else 0);recent=f.read().decode(errors='ignore')
  if 'ReflectorLogic: Authentication OK' in recent and pathlib.Path('/dev/shm/sqlink_dtmf').is_symlink():return True
 return False

def activate(db,p,boot=False):
 if not ready(p):raise ValueError('Complete the server port, login and password before activating.')
 if not boot:idle()
 old=CONFIG.read_bytes();st=CONFIG.stat();raw=render_config(old,p)
 BACKUPS.mkdir(parents=True,exist_ok=True);BACKUPS.chmod(0o700)
 tag=datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f')
 atomic(BACKUPS/(tag+'.conf'),old);write_json(BACKUPS/(tag+'.json'),db)
 write_json(BASE/'pending.json',dict(config=old.decode(),mode=st.st_mode&0o777,uid=st.st_uid,gid=st.st_gid,database=db))
 try:
  if not boot:logstat=LOG.stat()
  atomic(CONFIG,raw,st.st_mode&0o777,(st.st_uid,st.st_gid))
  if not boot:
   restart()
   if not authenticated(logstat.st_size,logstat.st_ino):raise RuntimeError('Authentication failed')
  new=copy.deepcopy(db);new['active']=p['id'];new['applied']=copy.deepcopy(p);save(new);publish(new);(BASE/'pending.json').unlink();db.clear();db.update(new)
 except Exception:
  recover()
  if not boot:
   try:restart()
   except Exception:raise ValueError('Previous configuration restored, but service restart failed. Check System.')
  raise ValueError('Connection failed. Previous profile and configuration restored.')

def dispatch(req):
 try:
  with locked() as db:
   action=req.get('action')
   if action=='profiles_snapshot':return dict(ok=True,**snapshot(db))
   if req.get('revision')!=revision(db):raise ValueError('Profiles changed. Reopen Profiles and try again.')
   p=next((p for p in db['profiles'] if p['id']==req.get('id')),None)
   if action=='profiles_save':
    if req.get('id') and p is None:raise ValueError('Profile not found.')
    if p is None and len(db['profiles'])>=12:raise ValueError('Maximum 12 profiles.')
    edited=validate(req.get('settings'),p)
    if any(x['id']!=edited['id'] and x['name'].casefold()==edited['name'].casefold() for x in db['profiles']):raise ValueError('Choose a unique profile name.')
    if p:p.clear();p.update(edited)
    else:db['profiles'].append(edited)
    save(db);message='Profile saved. Activate to apply its settings.'
   else:
    if p is None:raise ValueError('Profile not found.')
    if req.get('confirm') is not True:raise ValueError('Confirmation required.')
    if action=='profiles_activate':activate(db,p);message='Profile activated and connected.'
    elif action=='profiles_default':
     if not ready(p):raise ValueError('Complete this profile before making it the default.')
     db['default']=p['id'];save(db);message='Default profile saved for the next boot.'
    elif action=='profiles_delete':
     if p['id'] in (db['active'],db['default']):raise ValueError('Cannot delete the active or default profile.')
     BACKUPS.mkdir(parents=True,exist_ok=True);BACKUPS.chmod(0o700);write_json(BACKUPS/(datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f')+'-deleted.json'),db)
     db['profiles'].remove(p);save(db);message='Profile deleted.'
    else:raise ValueError('Unsupported profile action.')
   return dict(ok=True,message=message,**snapshot(db))
 except ValueError as exc:return dict(ok=False,message=str(exc))
 except Exception:return dict(ok=False,message='Profile service unavailable. Current configuration has been preserved; check System.')

if __name__=='__main__':
 import sys
 BOOTING='--boot' in sys.argv
 with locked() as db:
  if '--boot' in sys.argv:
   p=next(p for p in db['profiles'] if p['id']==db['default'])
   if ready(p):activate(db,p,boot=True)
  publish(db)
 print('Profile store ready; no credentials displayed.')
