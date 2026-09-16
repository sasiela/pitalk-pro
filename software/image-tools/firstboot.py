#!/usr/bin/python3
"""PiTalk Pro test image provisioning. Operates only on the newly flashed system."""
import configparser,json,os,pathlib,re,secrets,socket,subprocess,uuid
BOOT=pathlib.Path('/boot/firmware');STATE=pathlib.Path('/var/lib/pitalk')
def run(args,**kw):return subprocess.run(args,check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=90,**kw)
def validate(c):
 if not isinstance(c,dict):raise ValueError('Configuration must be a JSON object.')
 def text(key,default=''):
  v=c.get(key,default)
  if not isinstance(v,str) or any(ord(x)<32 for x in v):raise ValueError('Invalid field: '+key)
  return v
 password=text('system_password')
 if not 12<=len(password)<=128 or ':' in password:raise ValueError('system_password must contain 12-128 characters, without colon.')
 hostname=text('hostname')
 if hostname and not re.fullmatch(r'[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?',hostname):raise ValueError('Invalid hostname.')
 country=text('wifi_country','PL').upper()
 if not re.fullmatch('[A-Z]{2}',country):raise ValueError('wifi_country must be a two-letter country code.')
 ssid=text('wifi_ssid');wifi=text('wifi_password')
 if len(ssid.encode())>32:raise ValueError('Wi-Fi SSID is too long.')
 if ssid and not (8<=len(wifi)<=63 or re.fullmatch('[0-9a-fA-F]{64}',wifi)):raise ValueError('Wi-Fi password must contain 8-63 characters or 64 hex digits.')
 login=text('callsign');auth=text('reflector_password');host=text('reflector_host','sqlink.pl')
 if login and not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9/_-]{0,31}',login):raise ValueError('Invalid callsign.')
 if bool(login)!=bool(auth):raise ValueError('Set both callsign and reflector_password, or leave both empty.')
 if auth and (len(auth)>128 or any(ord(x)<33 or ord(x)>126 or x in '\\"' for x in auth)):raise ValueError('Invalid reflector password format.')
 if not re.fullmatch(r'[A-Za-z0-9.-]{1,253}',host):raise ValueError('Invalid reflector host.')
 tg=str(c.get('default_tg',0));mon=text('monitored_tgs');timeout=str(c.get('monitor_timeout',30))
 if not tg.isdigit() or not 0<=int(tg)<=4294967295:raise ValueError('Invalid default_tg.')
 if len(mon)>512 or any(not re.fullmatch(r'[1-9][0-9]{0,9}\+{0,3}',x) or int(x.rstrip('+'))>4294967295 for x in mon.split(',') if x):raise ValueError('Invalid monitored_tgs.')
 if not timeout.isdigit() or not 1<=int(timeout)<=86400:raise ValueError('Invalid monitor_timeout.')
 return dict(password=password,hostname=hostname,country=country,ssid=ssid,wifi=wifi,login=login,auth=auth,host=host,tg=tg,mon=mon,timeout=timeout)
def expand():
 try:
  root=subprocess.check_output(['findmnt','-n','-o','SOURCE','/'],text=True).strip()
  if root=='/dev/mmcblk0p2':
   subprocess.run(['growpart','/dev/mmcblk0','2'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=30)
   run(['resize2fs',root])
 except Exception:pass

def main():
 STATE.mkdir(mode=0o700,parents=True,exist_ok=True)
 run(['ssh-keygen','-A'])
 if (STATE/'initialized').exists():return
 status=BOOT/'PITALK-STATUS.txt';config=BOOT/'pitalk-setup.json'
 try:c=validate(json.loads(config.read_text()))
 except (ValueError,OSError):
  status.write_text('Setup not applied. Fill pitalk-setup.json: system_password (12+ characters). Wi-Fi and reflector fields are optional. See PITALK-README.txt. Then reboot.\n');return
 hostname=c['hostname'] or ('pitalk-'+pathlib.Path('/etc/machine-id').read_text().strip()[-6:])
 pathlib.Path('/etc/hostname').write_text(hostname+'\n');run(['hostname',hostname])
 pathlib.Path('/etc/hosts').write_text('127.0.0.1 localhost\n127.0.1.1 '+hostname+'\n::1 localhost ip6-localhost ip6-loopback\n')
 run(['chpasswd'],input=('sqlink:'+c['password']+'\n').encode())
 cert=pathlib.Path('/etc/sqlink-web');cert.mkdir(exist_ok=True)
 run(['openssl','req','-x509','-newkey','rsa:2048','-nodes','-days','3650','-keyout',str(cert/'key.pem'),'-out',str(cert/'cert.pem'),'-subj','/CN='+hostname+'.local','-addext','subjectAltName=DNS:'+hostname+'.local,DNS:'+hostname])
 os.chown(cert/'key.pem',0,1002);os.chmod(cert/'key.pem',0o640)
 pathlib.Path('/etc/modprobe.d/pitalk-wifi-country.conf').write_text('options cfg80211 ieee80211_regdom='+c['country']+'\n')
 import shutil
 if shutil.which('iw'):run(['iw','reg','set',c['country']])
 cmd=BOOT/'cmdline.txt';raw=cmd.read_text();raw=re.sub(r'\s*cfg80211.ieee80211_regdom=\S+','',raw).strip();cmd.write_text(raw+' cfg80211.ieee80211_regdom='+c['country']+'\n')
 if c['ssid']:
  keyfile=configparser.ConfigParser(interpolation=None)
  keyfile.read_dict({'connection':{'id':'PiTalk Wi-Fi','uuid':str(uuid.uuid4()),'type':'wifi','interface-name':'wlan0','autoconnect':'true','autoconnect-priority':'100'},'wifi':{'mode':'infrastructure','ssid':c['ssid']},'wifi-security':{'key-mgmt':'wpa-psk','psk':c['wifi']},'ipv4':{'method':'auto'},'ipv6':{'method':'auto'}})
  net=pathlib.Path('/etc/NetworkManager/system-connections/pitalk.nmconnection');net.parent.mkdir(parents=True,exist_ok=True)
  with net.open('w') as f:keyfile.write(f,space_around_delimiters=False)
  net.chmod(0o600);run(['nmcli','connection','load',str(net)]);run(['nmcli','radio','wifi','on'])
  subprocess.run(['nmcli','--wait','15','connection','up','PiTalk Wi-Fi'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=20)
 conf=pathlib.Path('/etc/svxlink/svxlink.conf');raw=conf.read_text();section='';result=[]
 edits={'SimplexLogic':{'CALLSIGN':c['login'] or 'NOCALL'},'ReflectorLogic':{'CALLSIGN':c['login'] or 'NOCALL','AUTH_KEY':('"'+c['auth']+'"') if c['auth'] else '','HOSTS':c['host'],'DEFAULT_TG':c['tg'],'MONITOR_TGS':c['mon'],'TG_SELECT_TIMEOUT':c['timeout']}}
 for line in raw.splitlines():
  match=re.match(r'\s*\[([^]]+)\]',line)
  if match:section=match[1]
  match=re.match(r'\s*([A-Z_]+)\s*=',line)
  if match and match[1] in edits.get(section,{}):line=match[1]+'='+edits[section][match[1]]
  result.append(line)
 conf.write_text('\n'.join(result)+'\n');conf.chmod(0o640);os.chown(conf,0,1002)
 expand()
 # Overwrite supplied secrets on the visible boot partition before removing the file.
 with config.open('r+b') as f:f.write(b' '*config.stat().st_size);f.flush();os.fsync(f.fileno())
 config.unlink();(STATE/'initialized').write_text('PiTalk Pro alpha-1\n')
 status.write_text('Setup complete. Host: '+hostname+'.local\nPanel: https://'+hostname+'.local:8443\nLogin: sqlink; password: the system_password you supplied.\n')
 os.sync()
if __name__=='__main__':
 try:main()
 except Exception:
  (BOOT/'PITALK-STATUS.txt').write_text('Setup failed. Check your configuration and reboot. No secret values are logged.\n')
  raise SystemExit(1)
