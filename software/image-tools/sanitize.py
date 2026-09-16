import pathlib,os,re,json,shutil,configparser,stat
B=pathlib.Path('/var/tmp/pitalk-image-alpha');R=B/'root';boot=B/'boot'
def remove(rel):
 p=R/rel
 if p.is_dir() and not p.is_symlink():shutil.rmtree(p)
 elif p.exists() or p.is_symlink():p.unlink()
def write(rel,text,mode=0o644):
 p=R/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text);p.chmod(mode)
# All operations target staging, never the running system.
for rel in ['root','home/OWNER_USER','var/lib/cloud','var/lib/bluetooth','var/lib/NetworkManager','var/lib/sqlink-bluetooth','var/lib/pitalk','var/lib/dbus/machine-id','var/lib/systemd/random-seed','var/lib/systemd/rfkill','etc/sqlink-web/key.pem','etc/sqlink-web/cert.pem','etc/sudoers.d/99-sqlink-temporary','etc/ssl/private/ssl-cert-snakeoil.key','etc/ssh/ssh_host_rsa_key','etc/ssh/ssh_host_rsa_key.pub','etc/ssh/ssh_host_ecdsa_key','etc/ssh/ssh_host_ecdsa_key.pub','etc/ssh/ssh_host_ed25519_key','etc/ssh/ssh_host_ed25519_key.pub','etc/svxlink/node_info.json']:
 remove(rel)
for pattern in ['etc/*-','etc/**/*.before-*','etc/**/*.bak','etc/**/*.old','usr/local/**/__pycache__','usr/lib/sqlink/**/__pycache__','opt/**/__pycache__','var/lib/sudo','var/lib/dhcpcd*','var/lib/dhcp','var/lib/lightdm','var/lib/systemd/linger/xeon','var/lib/apt/lists','etc/ssl/certs/ssl-cert-snakeoil.pem','var/spool/mail/*','etc/NetworkManager/system-connections/*','etc/NetworkManager/conf.d/*mac*']:
 for p in list(R.glob(pattern)):remove(str(p.relative_to(R)))
for name in ('passwd','shadow','group','gshadow','subuid','subgid'):
 p=R/'etc'/name;lines=[]
 for line in p.read_text().splitlines():
  f=line.split(':')
  if f[0]=='OWNER_USER':continue
  if name in ('shadow','gshadow'):f[1]='!'
  if name in ('group','gshadow'):f[-1]=','.join(x for x in f[-1].split(',') if x!='OWNER_USER')
  lines.append(':'.join(f))
 p.write_text('\n'.join(lines)+'\n')
write('etc/machine-id','');write('etc/hostname','pitalk\n');write('etc/hosts','127.0.0.1 localhost\n127.0.1.1 pitalk\n::1 localhost ip6-localhost ip6-loopback\n')
write('etc/cloud/cloud-init.disabled','PiTalk first-boot setup is used in this test image.\n')
write('etc/sudoers.d/90-pitalk-owner','sqlink ALL=(ALL:ALL) ALL\n',0o440)
write('etc/ssh/sshd_config.d/00-pitalk.conf','PermitRootLogin no\nPasswordAuthentication yes\nPermitEmptyPasswords no\nAllowUsers sqlink\n')
for rel,mode in [('dev',0o755),('proc',0o755),('sys',0o755),('run',0o755),('tmp',0o1777),('var/tmp',0o1777),('var/log',0o755),('var/cache',0o755),('var/backups',0o755),('root',0o700),('mnt',0o755),('media',0o755),('var/lib/NetworkManager',0o700),('var/lib/bluetooth',0o700),('var/lib/sqlink-bluetooth',0o700),('etc/NetworkManager/system-connections',0o700),('var/lib/pitalk',0o700),('var/lib/dbus',0o755)]:
 p=R/rel;p.mkdir(parents=True,exist_ok=True);p.chmod(mode)
(R/'var/lib/dbus/machine-id').symlink_to('/etc/machine-id')
for p in (R/'etc/svxlink').rglob('*'):
 if not p.is_file() or p.is_symlink():continue
 try:text=p.read_text()
 except UnicodeError:continue
 text=re.sub(r'(?m)^(\s*(?:AUTH_KEY|PASSWORD|SYSOPNAME|LOCATION|CALLSIGN)\s*=).*$',lambda m:m[1]+('NOCALL' if 'CALLSIGN' in m[1] else ''),text)
 text=text.replace('OWNER_CALLSIGN','NOCALL');p.write_text(text)
conf=R/'etc/svxlink/svxlink.conf';text=conf.read_text()
text=re.sub(r'(?m)^DEFAULT_TG=.*$','DEFAULT_TG=0',text);text=re.sub(r'(?m)^MONITOR_TGS=.*$','MONITOR_TGS=',text);conf.write_text(text);conf.chmod(0o640);os.chown(conf,0,1002)
# Owner-neutral screen defaults.
write('var/lib/sqlink-display/settings.json',json.dumps({'brightness':90,'color_scheme':'Ocean','idle_timeout':30})+'\n')
os.chown(R/'var/lib/sqlink-display',1002,1002);os.chown(R/'var/lib/sqlink-display/settings.json',1002,1002)
# Remove installation seed files containing original credentials.
for name in ('user-data','meta-data','network-config','firstrun.sh','userconf','userconf.txt','ssh','ssh.txt','wpa_supplicant.conf'):
 p=boot/name
 if p.exists():p.unlink()
p=boot/'cmdline.txt';s=p.read_text();s=re.sub(r'\s*ds=\S+','',s);s=re.sub(r'\s*cfg80211.ieee80211_regdom=\S+','',s);p.write_text(s.strip()+'\n')
shutil.copy(B/'payload/firstboot.py',R/'usr/local/sbin/pitalk-firstboot.py');(R/'usr/local/sbin/pitalk-firstboot.py').chmod(0o755)
shutil.copy(B/'payload/pitalk-setup.json',boot/'pitalk-setup.json');shutil.copy(B/'payload/PITALK-README.txt',boot/'PITALK-README.txt')
write('etc/systemd/system/pitalk-firstboot.service','''[Unit]
Description=PiTalk image initial configuration
Wants=NetworkManager.service
After=local-fs.target NetworkManager.service
Before=network-online.target ssh.service sqlink-web.service svxlink.service sqlink-screen.service
[Service]
Type=oneshot
ExecStart=/usr/bin/python3 /usr/local/sbin/pitalk-firstboot.py
RemainAfterExit=yes
TimeoutStartSec=180
[Install]
WantedBy=multi-user.target
''')
(R/'etc/systemd/system/multi-user.target.wants/pitalk-firstboot.service').symlink_to('../pitalk-firstboot.service')
for unit in ('svxlink','sqlink-web'):
 write('etc/systemd/system/'+unit+'.service.d/firstboot.conf','[Unit]\nAfter=pitalk-firstboot.service\nConditionPathExists=/var/lib/pitalk/initialized\n')
write('usr/local/sbin/pitalk-radio-ready.py','''#!/usr/bin/python3
import configparser,sys
c=configparser.ConfigParser(interpolation=None);c.read('/etc/svxlink/svxlink.conf');s=c['ReflectorLogic'];sys.exit(0 if s.get('AUTH_KEY','').strip('"') and s.get('CALLSIGN','NOCALL')!='NOCALL' else 1)
''',0o755)
write('etc/systemd/system/svxlink.service.d/ready.conf','[Service]\nExecCondition=/usr/bin/python3 /usr/local/sbin/pitalk-radio-ready.py\n')
write('etc/systemd/system/sqlink-web.service.d/audio.conf','''[Unit]
After=user@1002.service
Wants=user@1002.service
[Service]
BindReadOnlyPaths=
BindReadOnlyPaths=/run/user/1002:/run/sqlink-web-user
Environment=PULSE_SERVER=unix:/run/sqlink-web-user/pulse/native
''')
# Use the local interface addresses instead of a personal fixed subnet and hostname.
p=R/'opt/sqlink-web/server.py';s=p.read_text();a=s.index(' def local_access(self):');z=s.index(' def do_GET(self):',a)
s=s[:a]+''' def local_access(self):
  try:
   host=self.headers.get('Host','').split(':')[0].lower()
   interfaces=json.loads(run(['ip','-j','-4','addr','show']))
   addresses=[a for i in interfaces for a in i.get('addr_info',[]) if a.get('family')=='inet']
   client=ipaddress.ip_address(self.client_address[0])
   local=any(client in ipaddress.ip_network(a['local']+'/'+str(a['prefixlen']),strict=False) for a in addresses)
   return local and host in ({a['local'] for a in addresses}|{socket.gethostname(),socket.gethostname()+'.local'})
  except Exception:return False
''' +s[z:];p.write_text(s)
# Discard remnants of old machine IDs, history, swap and failed setup files.
for pattern in ('var/swap*','swapfile*','etc/ssh/ssh_host_*','var/lib/systemd/credential*','etc/systemd/system/sqlink-screen.service.d/demo.conf'):
 for p in list(R.glob(pattern)):remove(str(p.relative_to(R)))
# Rebuild compiled custom code only after sanitization.
for base in (R/'usr/lib/sqlink',R/'usr/local',R/'opt'):
 for p in list(base.rglob('*.pyc')):p.unlink()
print('Sanitized staging tree; application files retained.')
