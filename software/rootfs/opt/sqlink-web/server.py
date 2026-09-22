#!/usr/bin/python3
"""PiTalk Pro LAN management. TLS, LAN restriction, CSRF, bounded JSON APIs."""
import ipaddress
import json,os,pathlib,ssl,time,secrets,hashlib,hmac,threading,socket,subprocess,http.cookies,urllib.parse
from http.server import ThreadingHTTPServer,BaseHTTPRequestHandler
from sqlink import reflector,api,gpio,profile_state
import listen_audio
import audio_test
ROOT=pathlib.Path(__file__).parent/'static'
SESSIONS={};FAILURES={};LOCK=threading.Lock();MUTATE=threading.Lock()
def bridge(kind,payload):
 path='/run/sqlink-'+('wifi' if kind=='wifi' else 'bluetooth')+'/control.sock'
 with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM) as s:
  s.settimeout(115);s.connect(path);s.sendall((json.dumps(payload)+'\n').encode())
  with s.makefile('rb') as f:raw=f.readline(262145)
 if len(raw)>262144:raise ValueError('Response too large')
 return json.loads(raw)
def run(args):return subprocess.check_output(args,text=True,timeout=4,stderr=subprocess.DEVNULL).strip()
def state():
 online=reflector.is_connected();ptt=gpio.is_ptt_active() if gpio.available() else False
 tg=0;talker='';rx=False
 try:
  parts=pathlib.Path('/dev/shm/sqlink-radio-state').read_text().split(maxsplit=3)
  pid,tg,rx=map(int,parts[:3])
  if pid!=int(pathlib.Path('/run/svxlink.pid').read_text()):tg=0;rx=False
  elif len(parts)>3:talker=parts[3].strip()
 except (OSError,ValueError):pass
 mode='TX' if ptt else 'OFFLINE' if not online else 'RX' if rx else 'MONITOR' if tg==0 else 'IDLE'
 return dict(profile=profile_state.current().get("name", "Unknown"),online=online,mode=mode,tg=tg,talker=talker if mode=='RX' else '',callsign=reflector.get_callsign(),uptime=int(float(pathlib.Path('/proc/uptime').read_text().split()[0])),load=os.getloadavg()[0])
def diagnostics():
 units=['svxlink','sqlink-screen','sqlink-ptt-button','sqlink-bluetooth-helper','sqlink-wifi-helper','sqlink-web']
 services={}
 for u in units:
  try:services[u]=run(['systemctl','is-active',u+'.service'])
  except Exception:services[u]='inactive'
 log=reflector.read_recent_log(16384).splitlines()
 keys=('Authentication OK','Disconnected from','Heartbeat timeout','Selecting TG','Talker start','Talker stop','Error message','SIGHUP')
 return dict(services=services,events=[x for x in log if any(k in x for k in keys)][-30:],state=state())

ACTIVITY_NODES = {}
ACTIVITY_CACHE = None
ACTIVITY_TIME = 0
ACTIVITY_LOCK = threading.Lock()
ACTIVITY_PROFILE = None
def normalize_activity(data):
 nodes=data.get('statusNodes')
 if not isinstance(nodes,dict):raise ValueError('No station status available')
 result={};idle=[];visible=0
 def group(tg):return result.setdefault(tg,dict(tg=tg,connected=[],monitoring=[],talkers=[]))
 def number(v):
  try:return int(str(v).rstrip('+'))
  except (ValueError,TypeError):return 0
 for callsign,node in nodes.items():
  if not isinstance(node,dict) or node.get('hidden') is True:continue
  visible+=1;tg=number(node.get('tg'));callsign=str(callsign)
  if tg>0:
   group(tg)['connected'].append(callsign)
   if node.get('isTalker') is True:group(tg)['talkers'].append(callsign)
  else:idle.append(callsign)
  monitors=node.get('monitoredTGs',[])
  if isinstance(monitors,list):
   for monitored in set(number(x) for x in monitors):
    if monitored>0 and monitored!=tg:group(monitored)['monitoring'].append(callsign)
 for g in result.values():
  for k in ('connected','monitoring','talkers'):g[k].sort()
 return dict(groups=sorted(result.values(),key=lambda g:(not bool(g['talkers']),-len(g['connected']),g['tg'])),idle=sorted(idle),stations=visible,updated_at=time.time(),stale=False)
def activity():
 global ACTIVITY_CACHE,ACTIVITY_TIME,ACTIVITY_NODES,ACTIVITY_PROFILE
 with ACTIVITY_LOCK:
  key=profile_state.key()
  if ACTIVITY_PROFILE!=key:
   ACTIVITY_CACHE=None;ACTIVITY_NODES={};ACTIVITY_TIME=0;ACTIVITY_PROFILE=key
  if profile_state.current().get('directory')!='sqlink':
   return dict(groups=[],idle=[],stations=0,updated_at=time.time(),stale=False,available=False,message='Station directory is not configured for this profile.')
  if ACTIVITY_CACHE is not None and time.monotonic()-ACTIVITY_TIME<5:return ACTIVITY_CACHE
  try:
   data=api._get_json(api.STATUS_URL,timeout=5)
   ACTIVITY_CACHE=normalize_activity(data);ACTIVITY_TIME=time.monotonic()
   ACTIVITY_NODES={str(k):v for k,v in data['statusNodes'].items() if isinstance(v,dict) and v.get('hidden') is not True}
  except Exception:
   if ACTIVITY_CACHE is None:raise
   ACTIVITY_CACHE=dict(ACTIVITY_CACHE,stale=True);ACTIVITY_TIME=time.monotonic()
  return ACTIVITY_CACHE

def station_details(callsign):
 if not isinstance(callsign,str) or not 1<=len(callsign)<=128:raise ValueError('Invalid callsign')
 status=activity()
 node=ACTIVITY_NODES.get(callsign)
 if node is None:return dict(available=False,message='Station is no longer listed by the reflector.')
 # Only fields intentionally published as station information; never credentials.
 allowed=('tg','monitoredTGs','isTalker','nodeClass','nodeLocation','sysop','sw','swVer','projVer','protoVer','restrictedTG','qth','toneToTalkgroup','machineArch','CTCSS','DefaultTG','Echolink','Location','Locator','Mode','RXFREQ','TXFREQ','Type','Website','LinkedTo')
 def clean(value):
  if isinstance(value,dict):return {str(k):clean(v) for k,v in value.items() if not any(word in str(k).lower() for word in ('password','passwd','secret','auth','token','credential','key'))}
  if isinstance(value,list):return [clean(v) for v in value]
  return value
 return dict(available=True,callsign=callsign,config=clean({k:node[k] for k in allowed if k in node}),stale=status['stale'],updated_at=status['updated_at'])

class Handler(BaseHTTPRequestHandler):
 server_version='PiTalk'
 def log_message(self,*args):pass
 def reply(self,status,obj,cookie=None):
  raw=json.dumps(obj).encode();self.send_response(status);self.headers_common();self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(raw)))
  if cookie:self.send_header('Set-Cookie',cookie)
  self.end_headers();self.wfile.write(raw)
 def headers_common(self):
  self.send_header('Cache-Control','no-store');self.send_header('X-Content-Type-Options','nosniff');self.send_header('Referrer-Policy','no-referrer');self.send_header('X-Frame-Options','DENY')
  self.send_header('Content-Security-Policy',"default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'")
 def session(self):
  try:c=http.cookies.SimpleCookie(self.headers.get('Cookie',''));key=c['session'].value
  except Exception:return None
  with LOCK:
   s=SESSIONS.get(key)
   if not s or s['expires']<time.time():SESSIONS.pop(key,None);return None
   return key,s
 def local_access(self):
  host=self.headers.get('Host','').split(':')[0].lower()
  return ipaddress.ip_address(self.client_address[0]) in ipaddress.ip_network('192.168.1.0/24') and host in ('192.168.1.100','pitalk-pro','pitalk-pro.local')
 def do_GET(self):
  try:
   if not self.local_access():return self.reply(403,dict(ok=False,message='Local network access only.'))
   path=urllib.parse.urlsplit(self.path).path
   if path in ('/','/app.js','/style.css','/listen-worklet.js'):
    f=ROOT/({'/':'index.html'}.get(path,path[1:]));raw=f.read_bytes();self.send_response(200);self.headers_common();self.send_header('Content-Type',{'html':'text/html; charset=utf-8','js':'application/javascript','css':'text/css'}[f.suffix[1:]]);self.send_header('Content-Length',str(len(raw)));self.end_headers();self.wfile.write(raw);return
   session=self.session()
   if not session:return self.reply(401,{'ok':False,'message':'Please sign in.'})
   if path=='/api/listen':
    if not hmac.compare_digest(self.headers.get('X-CSRF-Token',''),session[1]['csrf']):return self.reply(403,dict(ok=False,message='Reload the page before listening.'))
    return listen_audio.stream(self)
   routes={'/api/profiles':lambda:bridge('wifi',{'action':'profiles_snapshot'}),'/api/audio-test':lambda:audio_test.snapshot(session[0]),'/api/session':lambda:dict(csrf=session[1]['csrf']),'/api/state':state,'/api/groups':api.get_talkgroups,'/api/activity':activity,'/api/station':lambda:station_details(urllib.parse.parse_qs(urllib.parse.urlsplit(self.path).query).get('callsign',[''])[0]),'/api/audio':lambda:bridge('bt',{'action':'status'}),'/api/bluetooth':lambda:bridge('bt',{'action':'status'}),'/api/challenge':lambda:bridge('bt',{'action':'challenge'}),'/api/wifi':lambda:bridge('wifi',{'action':'snapshot'}),'/api/user':lambda:bridge('wifi',{'action':'user_snapshot'}),'/api/system':diagnostics}
   if path not in routes:return self.reply(404,{'ok':False})
   self.reply(200,dict(ok=True,data=routes[path]()))
  except (BrokenPipeError,ConnectionResetError):pass
  except Exception:self.reply(503,dict(ok=False,message='Device service unavailable. Please retry.'))
 def do_POST(self):
  try:
   if not self.local_access():return self.reply(403,dict(ok=False,message='Local network access only.'))
   origin=self.headers.get('Origin');host=self.headers.get('Host','')
   if origin and origin!='https://'+host:return self.reply(403,{'ok':False,'message':'Origin rejected.'})
   if self.headers.get('Content-Type','').split(';')[0]!='application/json':return self.reply(415,{'ok':False})
   length=int(self.headers.get('Content-Length','0'))
   if not 0<length<=8192:return self.reply(413,{'ok':False})
   p=json.loads(self.rfile.read(length));path=urllib.parse.urlsplit(self.path).path
   if not isinstance(p,dict):raise ValueError()
   if path=='/api/login':
    ip=self.client_address[0];now=time.time()
    with LOCK:
     failures=[t for t in FAILURES.get(ip,[]) if now-t<900];FAILURES[ip]=failures
     if len(failures)>=8:return self.reply(429,dict(ok=False,message='Too many attempts. Try again in 15 minutes.'))
     failures.append(now)
    username=p.get('username','');password=p.get('password','')
    if username!='sqlink' or not isinstance(password,str) or not password or len(password)>512:
     return self.reply(401,dict(ok=False,message='Incorrect username or password.'))
    result=bridge('wifi',dict(action='web_auth',username=username,password=password))
    p.pop('password',None);password=''
    if not result.get('authenticated'):return self.reply(401,dict(ok=False,message='Incorrect username or password.'))
    token=secrets.token_urlsafe(32);csrf=secrets.token_urlsafe(32)
    with LOCK:
     for key,value in list(SESSIONS.items()):
      if value['expires']<now:SESSIONS.pop(key,None)
     if len(SESSIONS)>100:SESSIONS.clear()
     SESSIONS[token]=dict(csrf=csrf,expires=now+28800);FAILURES.pop(ip,None)
    return self.reply(200,dict(ok=True,csrf=csrf),'session='+token+'; Secure; HttpOnly; SameSite=Strict; Path=/; Max-Age=28800')
   session=self.session()
   if not session:return self.reply(401,dict(ok=False,message='Please sign in.'))
   if not hmac.compare_digest(self.headers.get('X-CSRF-Token',''),session[1]['csrf']):return self.reply(403,dict(ok=False,message='Session validation failed. Reload the page.'))
   if path=='/api/logout':
    audio_test.stop(session[0])
    with LOCK:SESSIONS.pop(session[0],None)
    return self.reply(200,dict(ok=True),'session=; Secure; HttpOnly; SameSite=Strict; Path=/; Max-Age=0')
   if path=='/api/audio-test':
    if p.get('action')=='start':result=audio_test.start(session[0],p.get('mode'))
    elif p.get('action')=='stop':
     audio_test.stop(session[0],p.get('id'));result=audio_test.snapshot(session[0])
    else:raise ValueError('Unsupported audio test action.')
    return self.reply(200,dict(ok=True,data=result))
   # Pairing confirmations must remain available while a Pair request waits.
   if path=='/api/bt' and p.get('action') in ('answer','cancel_pair'):
    return self.reply(200,bridge('bt',p))
   if not MUTATE.acquire(False):return self.reply(409,dict(ok=False,message='Another change is in progress.'))
   try:
    if path=='/api/tg':
     tg=str(p.get('tg',''))
     if not tg.isdigit() or not 0<=int(tg)<=4294967295:raise ValueError('Invalid talk group.')
     reflector.select_tg(tg);result=dict(ok=True,message='Talk group selected.')
    elif path=='/api/bt':
     if p.get('action') not in ('scan','pair','connect','disconnect','forget','auto','power','volume','transport','route','profile'):raise ValueError('Unsupported Bluetooth action.')
     result=bridge('bt',p)
    elif path=='/api/wifi':
     if p.get('action') not in ('scan','connect','set_default'):raise ValueError('Unsupported Wi-Fi action.')
     result=bridge('wifi',p)
    elif path=='/api/profiles':
     if p.get('action') not in ('profiles_save','profiles_activate','profiles_default','profiles_delete'):raise ValueError('Unsupported profile action.')
     result=bridge('wifi',p)
    elif path=='/api/user':
     p['action']='user_save';result=bridge('wifi',p)
    elif path=='/api/reboot':result=bridge('wifi',dict(action='restart_device',confirm=p.get('confirm') is True))
    else:return self.reply(404,dict(ok=False))
    self.reply(200,result)
   finally:MUTATE.release()
  except ValueError as e:self.reply(400,dict(ok=False,message=str(e) or 'Invalid request.'))
  except (BrokenPipeError,ConnectionResetError):pass
  except Exception:self.reply(503,dict(ok=False,message='Action failed. Refresh device status before retrying.'))

class Server(ThreadingHTTPServer):
 daemon_threads=True
 slots=threading.BoundedSemaphore(20)
 def process_request(self,request,address):
  if not self.slots.acquire(False):request.close();return
  try:super().process_request(request,address)
  except Exception:self.slots.release();raise
 def process_request_thread(self,request,address):
  try:super().process_request_thread(request,address)
  finally:self.slots.release()
 def get_request(self):
  s,addr=super().get_request();s.settimeout(5)
  try:
   s=self.context.wrap_socket(s,server_side=True);s.settimeout(120);return s,addr
  except Exception:s.close();raise
if __name__=='__main__':
 context=ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER);context.minimum_version=ssl.TLSVersion.TLSv1_2;context.load_cert_chain('/etc/sqlink-web/cert.pem','/etc/sqlink-web/key.pem')
 server=Server(('0.0.0.0',8443),Handler);server.context=context;server.serve_forever()
