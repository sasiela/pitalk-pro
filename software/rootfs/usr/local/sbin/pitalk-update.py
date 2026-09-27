#!/usr/bin/python3
"""Restricted PiTalk application updater. GitHub HTTPS, fixed paths, crash rollback."""
import ssl,urllib.error
import hashlib,json,os,pwd,re,shutil,socket,socketserver,subprocess,threading,time,urllib.request
from pathlib import Path
ROOT=Path('/var/lib/pitalk-update')
SOCKET='/run/pitalk-update/control.sock'
BASE='https://raw.githubusercontent.com/sasiela/pitalk-pro/'
ALLOWED={'usr/local/bin/sqlink-screen.py','usr/lib/sqlink/encoder.py','usr/lib/sqlink/encoder_volume.py','usr/lib/sqlink/update_ui.py'}
LEGACY=set(ALLOWED)
ALLOWED |= {'opt/sqlink-web/server.py','opt/sqlink-web/audio_test.py','opt/sqlink-web/listen_audio.py','opt/sqlink-web/static/app.js','opt/sqlink-web/static/style.css','opt/sqlink-web/static/index.html','opt/sqlink-web/static/listen-worklet.js'}
lock=threading.Lock()
state={'busy':False,'message':'Ready','available':None}

def atomic(path,data,mode=0o644):
    path=Path(path);tmp=path.with_name(path.name+'.update-tmp')
    with open(tmp,'wb') as f:
        f.write(data);f.flush();os.fsync(f.fileno())
    os.chmod(tmp,mode);os.replace(tmp,path)
    fd=os.open(path.parent,os.O_RDONLY)
    try:os.fsync(fd)
    finally:os.close(fd)

def save(name,value):atomic(ROOT/name,json.dumps(value).encode(),0o600)
def read(name,default=None):
    try:return json.loads((ROOT/name).read_text())
    except FileNotFoundError:return default

def download(url,limit=2000000):
    with urllib.request.urlopen(url,timeout=25) as r:
        data=r.read(limit+1)
    if len(data)>limit:raise ValueError('Download too large')
    return data

def manifest(tag):
    if not re.fullmatch(r'pitalk-v\d+\.\d+\.\d+',tag):raise ValueError('Invalid release tag')
    m=json.loads(download(BASE+tag+'/software/updates/release.json',50000))
    if m.get('tag')!=tag or m.get('format')!=1:raise ValueError('Unsupported release')
    if set(m.get('files',{})) not in (LEGACY,ALLOWED):raise ValueError('Unsupported file list')
    for v in m['files'].values():
        if not re.fullmatch('[a-f0-9]{64}',v):raise ValueError('Invalid checksum')
    return m

def guard():
    if Path('/sys/class/gpio/gpio536/value').read_text().strip()!='1':raise RuntimeError('Release PTT first')
    radio=Path('/dev/shm/sqlink-radio-state').read_text().split()
    pid=Path('/run/svxlink.pid').read_text().strip()
    if len(radio)<3 or radio[0]!=pid:raise RuntimeError('Radio state unavailable')
    if radio[2]!='0':raise RuntimeError('Wait until reception ends')
    if shutil.disk_usage(ROOT).free<50*1024*1024:raise RuntimeError('Not enough free space')

def restart():subprocess.run(['systemctl','restart','sqlink-screen','sqlink-web'],check=True,timeout=25)

def web_healthy():
    try:
        if subprocess.check_output(['systemctl','is-active','sqlink-web'],text=True,timeout=5).strip()!='active':return False
        # Loopback is deliberately rejected by the LAN policy; a bounded TLS
        # response verifies the listener without weakening access or logging in.
        try:
            urllib.request.urlopen('https://127.0.0.1:8443/api/session',context=ssl._create_unverified_context(),timeout=3)
        except urllib.error.HTTPError as e:return e.code in (401,403)
        return False
    except Exception:return False


def healthy(timeout=75):
    end=time.monotonic()+timeout;first=None;last_pid=None
    while time.monotonic()<end:
        try:
            pid=int(subprocess.check_output(['systemctl','show','sqlink-screen','--property=MainPID','--value'],text=True,timeout=5))
            h=json.loads(Path('/run/sqlink-ui/update-heartbeat.json').read_text())
            ok=pid>0 and h['pid']==pid and 0<=time.time()-h['time']<8 and web_healthy()
            if not ok or pid!=last_pid:first=None
            if ok:
                if first is None:first=time.monotonic()
                if time.monotonic()-first>=20:return True
            last_pid=pid
        except Exception:first=None
        time.sleep(2)
    return False

def restore(j):
    for name,entry in j['backup'].items():
        dest=Path('/')/name
        if entry['exists']:atomic(dest,(ROOT/'backup'/name).read_bytes(),entry['mode'])
        elif dest.exists():dest.unlink()
    save('installed.json',j['previous'])

def apply(m, staged):
    guard()
    backup=ROOT/'backup'
    if backup.exists():shutil.rmtree(backup)
    entries={}
    for name in sorted(staged):
        p=Path('/')/name;exists=p.exists();entries[name]={'exists':exists,'mode':p.stat().st_mode&0o777 if exists else 0o644}
        if exists:
            dest=backup/name;dest.parent.mkdir(parents=True,exist_ok=True);atomic(dest,p.read_bytes(),0o600)
    j={'previous':read('installed.json',{'tag':'bootstrap'}),'backup':entries}
    save('pending.json',j) # Durable journal before touching live files.
    try:
        for name in sorted(staged):atomic(Path('/')/name,staged[name],entries[name]['mode'])
        restart()
        if not healthy():raise RuntimeError('Screen or web health check failed')
        save('installed.json',{'tag':m['tag']});(ROOT/'pending.json').unlink()
    except Exception:
        restore(j);restart()
        recovered=healthy()
        if recovered:(ROOT/'pending.json').unlink()
        raise RuntimeError('Update failed; previous version restored' if recovered else 'Recovery needs attention')

def check():
    channel=json.loads(download(BASE+'main/software/updates/stable.json',10000))
    m=manifest(channel['tag']);state['available']=m['tag'];state['message']='Up to date' if m['tag']==read('installed.json',{}).get('tag') else 'Update available: '+m['tag']
    return m

def work(action):
    try:
        if action=='check':check()
        else:
            guard();m=check()
            if m['tag']==read('installed.json',{}).get('tag'):return
            data={}
            for name,digest in m['files'].items():
                b=download(BASE+m['tag']+'/software/rootfs/'+name)
                if hashlib.sha256(b).hexdigest()!=digest:raise ValueError('Checksum mismatch')
                if name.endswith('.py'):compile(b,name,'exec')
                data[name]=b
            state['message']='Installing; checking services...';apply(m,data);state['message']='Installed '+m['tag']
    except Exception as exc:
        state['message']=str(exc)[:160]
    finally:state['busy']=False;lock.release()

class Handler(socketserver.StreamRequestHandler):
    def handle(self):
        self.connection.settimeout(5)
        try:
            q=json.loads(self.rfile.readline(2049));action=q.get('action')
            if action not in ('status','check','install'):raise ValueError('Invalid action')
            if action=='install' and q.get('confirm') is not True:raise ValueError('Confirmation required')
            if action!='status':
                if not lock.acquire(False):raise ValueError('Update already running')
                state['busy']=True;state['message']='Checking...' if action=='check' else 'Preparing update...'
                threading.Thread(target=work,args=(action,),daemon=True).start()
            result=dict(state,installed=read('installed.json',{}).get('tag','bootstrap'),ok=True)
        except Exception as exc:result={'ok':False,'message':str(exc)[:160]}
        self.wfile.write(json.dumps(result).encode()+b'\n')

if __name__=='__main__':
    ROOT.mkdir(mode=0o700,parents=True,exist_ok=True)
    pending=read('pending.json')
    if pending:
        restore(pending);restart()
        if not healthy():raise RuntimeError('Recovery screen failed')
        (ROOT/'pending.json').unlink()
    Path(SOCKET).unlink(missing_ok=True)
    with socketserver.UnixStreamServer(SOCKET,Handler) as server:
        os.chown(SOCKET,0,pwd.getpwnam('sqlink').pw_gid);os.chmod(SOCKET,0o660)
        server.serve_forever()
