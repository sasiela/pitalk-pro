#!/usr/bin/python3
"""SQLink Bluetooth agent and narrowly scoped audio control."""
import os,json,pathlib,pwd,grp,re,socketserver,subprocess,threading,time,uuid
import dbus,dbus.service
from dbus.mainloop.glib import DBusGMainLoop, threads_init
from dbus.mainloop import NULL_MAIN_LOOP
from gi.repository import GLib

SOCKET='/run/sqlink-bluetooth/control.sock'
PREF=pathlib.Path('/var/lib/sqlink-bluetooth/preferences.json')
ADAPTER='org.bluez.Adapter1';DEVICE='org.bluez.Device1';PROPS='org.freedesktop.DBus.Properties'
LOCK=threading.Lock();STATE_LOCK=threading.Lock()
PAIR_TARGET=None;CHALLENGE=None;CALLBACKS=None
PREFERENCES={}
SUSPENDED=set()

class Rejected(dbus.DBusException):
    _dbus_error_name='org.bluez.Error.Rejected'


def run(args,timeout=10):
    r=subprocess.run(args,capture_output=True,text=True,timeout=timeout,env=dict(os.environ,LC_ALL='C'))
    if r.returncode:raise RuntimeError('Operation failed. Try again.')
    return r.stdout.strip()


def audio(*args):
    uid=pwd.getpwnam('sqlink').pw_uid
    return run(['/usr/sbin/runuser','-u','sqlink','--','/usr/bin/env',f'XDG_RUNTIME_DIR=/run/user/{uid}','/usr/bin/pactl',*map(str,args)])


def objects():
    bus=dbus.SystemBus(private=True, mainloop=NULL_MAIN_LOOP)
    try:return dict(dbus.Interface(bus.get_object('org.bluez','/'),'org.freedesktop.DBus.ObjectManager').GetManagedObjects(timeout=8))
    finally:bus.close()


def call(path,interface,method,*args,timeout=15):
    bus=dbus.SystemBus(private=True, mainloop=NULL_MAIN_LOOP)
    try:return getattr(dbus.Interface(bus.get_object('org.bluez',path),interface),method)(*args,timeout=timeout)
    finally:bus.close()


def adapter():
    return next((str(p) for p,v in objects().items() if ADAPTER in v),None)


def device(mac):
    if not isinstance(mac,str) or not re.fullmatch(r'[0-9A-Fa-f]{2}(?::[0-9A-Fa-f]{2}){5}',mac):raise ValueError('Invalid device.')
    for path,ifs in objects().items():
        if DEVICE in ifs and str(ifs[DEVICE].get('Address','')).upper()==mac.upper():return str(path),ifs[DEVICE]
    raise ValueError('Device not found. Scan again.')


def idle_audio():
    if pathlib.Path('/sys/class/gpio/gpio536/value').read_text().strip()!='1':raise ValueError('Release PTT first.')


def save():
    PREF.parent.mkdir(parents=True,exist_ok=True)
    tmp=PREF.with_suffix('.tmp');tmp.write_text(json.dumps(PREFERENCES));tmp.chmod(0o600);os.replace(tmp,PREF)


def audio_status():
    sinks=json.loads(audio('-f','json','list','sinks'));sources=json.loads(audio('-f','json','list','sources'))
    cards=json.loads(audio('-f','json','list','cards'))
    return dict(sinks=[dict(name=x['name'],label=x.get('description',x['name']),volume=round(max((v['value'] for v in x.get('volume',{}).values()),default=0)*100/65536),mute=bool(x.get('mute'))) for x in sinks],
                sources=[dict(name=x['name'],label=x.get('description',x['name'])) for x in sources if not x['name'].endswith('.monitor')],
                sink=audio('get-default-sink'),source=audio('get-default-source'),
                cards=[dict(name=c['name'],active=c.get('active_profile'),
                    profiles=[dict(name=n,label=v.get('description',n)) for n,v in c.get('profiles',{}).items()
                              if n!='off' and v.get('available') not in (False,'no')]) for c in cards if c['name'].startswith('bluez_card.')])


def snapshot():
    all_objects=objects();a=next((v[ADAPTER] for v in all_objects.values() if ADAPTER in v),{})
    devices=[]
    for path,ifs in all_objects.items():
        if DEVICE not in ifs:continue
        d=ifs[DEVICE];mac=str(d.get('Address',''));uuids=[str(u) for u in d.get('UUIDs',[])]
        devices.append(dict(mac=mac,name=str(d.get('Alias',d.get('Name',mac))),paired=bool(d.get('Paired',False)),
            connected=bool(d.get('Connected',False)),trusted=bool(d.get('Trusted',False)),
            rssi=int(d.get('RSSI',-127)),audio=any(u[4:8] in ('1108','110a','110b','111e','111f') for u in uuids),
            auto=mac in PREFERENCES.get('auto',[])))
    devices.sort(key=lambda d:(not d['connected'],not d['paired'],not d['audio'],-d['rssi'],d['name']))
    result=dict(available=bool(a),powered=bool(a.get('Powered',False)),scanning=bool(a.get('Discovering',False)),devices=devices)
    try:result['audio']=audio_status()
    except Exception:result['audio']=dict(error='Audio service unavailable.',sinks=[],sources=[],cards=[])
    return result


def set_route(kind,name,persist=True):
    idle_audio();st=audio_status();nodes=st['sinks' if kind=='sink' else 'sources']
    if name not in {n['name'] for n in nodes}:raise ValueError('Audio device unavailable.')
    old=st[kind];plural='sink-inputs' if kind=='sink' else 'source-outputs';verb='move-sink-input' if kind=='sink' else 'move-source-output'
    streams=json.loads(audio('-f','json','list',plural));moved=[]
    try:
        audio('set-default-'+kind,name)
        for stream in streams:
            if 'svxlink' in str(stream.get('properties',{})).lower():
                audio(verb,stream['index'],name);moved.append(stream)
        if persist:PREFERENCES[kind]=name;save()
    except Exception:
        try:
            audio('set-default-'+kind,old)
            for stream in moved:audio(verb,stream['index'],str(stream[kind]))
        except Exception:pass
        raise


def select_transport(transport):
    idle_audio()
    if transport not in ('usb','bluetooth'):raise ValueError('Invalid audio device.')
    before=audio_status();old_preferences=json.loads(json.dumps(PREFERENCES));changed=None
    prefix='alsa_output.usb-' if transport=='usb' else 'bluez_output.'
    source_prefix='alsa_input.usb-' if transport=='usb' else 'bluez_input.'
    def pair(st):
        for sink in st['sinks']:
            if not sink['name'].startswith(prefix):continue
            key=sink['name'][len(prefix):].split('.')[0]
            if transport=='bluetooth':
                # PipeWire may name the sink with underscores and the source with colons.
                key=key.replace('_',':').upper()
                source=next((n for n in st['sources'] if n['name'].startswith(source_prefix)
                    and n['name'][len(source_prefix):].split('.')[0].replace('_',':').upper()==key),None)
            else:
                source=next((n for n in st['sources'] if n['name'].startswith(source_prefix+key+'.')),None)
            if source:return sink['name'],source['name']
        return None
    try:
        st=before;target=pair(st)
        if not target and transport=='bluetooth':
            for card in st['cards']:
                profiles=[x['name'] for x in card['profiles'] if x['name'].startswith('headset-head-unit') or x['name'].startswith('handsfree-head-unit')]
                if profiles:
                    changed=(card['name'],card['active'])
                    audio('set-card-profile',card['name'],profiles[0])
                    for _ in range(20):
                        time.sleep(0.25);target=pair(audio_status())
                        if target:break
                    if target:PREFERENCES.setdefault('profiles',{})[card['name']]=profiles[0]
                    break
        if not target:
            raise ValueError('Connect a Bluetooth headset in Menu > Bluetooth first. A microphone profile is required.' if transport=='bluetooth' else 'USB audio card with microphone not available.')
        set_route('sink',target[0],False);set_route('source',target[1],False)
        PREFERENCES.update(sink=target[0],source=target[1]);save()
    except Exception:
        if changed:
            try:audio('set-card-profile',changed[0],changed[1]);time.sleep(1)
            except Exception:pass
        for kind in ('sink','source'):
            try:set_route(kind,before[kind],False)
            except Exception:pass
        PREFERENCES.clear();PREFERENCES.update(old_preferences)
        raise


def clear_challenge(reject=False):
    global CHALLENGE,CALLBACKS
    with STATE_LOCK:
        cb=CALLBACKS;CHALLENGE=None;CALLBACKS=None
    if reject and cb:
        GLib.idle_add(lambda:cb[1](Rejected('Cancelled')))


def answer(req):
    global CHALLENGE,CALLBACKS
    with STATE_LOCK:
        challenge=CHALLENGE;callbacks=CALLBACKS
        if not challenge or req.get('id')!=challenge['id'] or not callbacks:raise ValueError('Pairing request expired.')
        value=req.get('value','')
        if req.get('accept') and challenge['kind'] in ('pin','passkey'):
            if not isinstance(value,str) or not value.isdigit() or not 1<=len(value)<= (6 if challenge['kind']=='passkey' else 16):raise ValueError('Enter the numeric PIN.')
        CHALLENGE=None;CALLBACKS=None
    def reply():
        if not req.get('accept'):callbacks[1](Rejected('User rejected pairing'))
        elif challenge['kind']=='pin':callbacks[0](value)
        elif challenge['kind']=='passkey':callbacks[0](dbus.UInt32(int(value)))
        else:callbacks[0]()
        return False
    GLib.idle_add(reply)


class Agent(dbus.service.Object):
    def check(self,path):
        if str(path)!=PAIR_TARGET:raise Rejected('Pair only from the device menu')
    def prompt(self,path,kind,code,reply,error):
        global CHALLENGE,CALLBACKS
        try:self.check(path)
        except Rejected as e:error(e);return
        with STATE_LOCK:
            CHALLENGE=dict(id=str(uuid.uuid4()),kind=kind,code=code)
            CALLBACKS=(reply,error)
    @dbus.service.method('org.bluez.Agent1',in_signature='ou',out_signature='',async_callbacks=('reply','error'))
    def RequestConfirmation(self,path,passkey,reply,error):self.prompt(path,'confirm',f'{int(passkey):06}',reply,error)
    @dbus.service.method('org.bluez.Agent1',in_signature='o',out_signature='',async_callbacks=('reply','error'))
    def RequestAuthorization(self,path,reply,error):self.prompt(path,'confirm','',reply,error)
    @dbus.service.method('org.bluez.Agent1',in_signature='o',out_signature='s',async_callbacks=('reply','error'))
    def RequestPinCode(self,path,reply,error):self.prompt(path,'pin','',reply,error)
    @dbus.service.method('org.bluez.Agent1',in_signature='o',out_signature='u',async_callbacks=('reply','error'))
    def RequestPasskey(self,path,reply,error):self.prompt(path,'passkey','',reply,error)
    @dbus.service.method('org.bluez.Agent1',in_signature='os',out_signature='')
    def DisplayPinCode(self,path,pincode):
        global CHALLENGE
        self.check(path)
        with STATE_LOCK:CHALLENGE=dict(id=str(uuid.uuid4()),kind='display',code=str(pincode))
    @dbus.service.method('org.bluez.Agent1',in_signature='ouq',out_signature='')
    def DisplayPasskey(self,path,passkey,entered):self.DisplayPinCode(path,f'{int(passkey):06}')
    @dbus.service.method('org.bluez.Agent1',in_signature='os',out_signature='')
    def AuthorizeService(self,path,service):
        if str(path)==PAIR_TARGET:return
        d=objects().get(path,{}).get(DEVICE,{})
        if not d.get('Trusted'):raise Rejected('Device is not trusted')
    @dbus.service.method('org.bluez.Agent1',in_signature='',out_signature='')
    def Cancel(self):clear_challenge()
    @dbus.service.method('org.bluez.Agent1',in_signature='',out_signature='')
    def Release(self):clear_challenge(True)


def dispatch(req):
    global PAIR_TARGET
    action=req.get('action')
    if action=='challenge':
        with STATE_LOCK:return dict(ok=True,challenge=CHALLENGE)
    if action=='answer':answer(req);return dict(ok=True)
    if action=='cancel_pair':
        target=PAIR_TARGET;clear_challenge(True)
        if target:
            try:call(target,DEVICE,'CancelPairing')
            except Exception:pass
        return dict(ok=True)
    if action=='status':return dict(ok=True,status=snapshot())
    if not LOCK.acquire(blocking=False):return dict(ok=False,message='Another operation is running.')
    try:
        if action in ('power','scan'):
            idle_audio();a=adapter()
            if not a:raise ValueError('Bluetooth adapter not found.')
            on=action=='scan' or req.get('on') is True
            if on:run(['/usr/sbin/rfkill','unblock','bluetooth'])
            call(a,PROPS,'Set',ADAPTER,'Powered',dbus.Boolean(on))
            if action=='scan':
                scan_bus=dbus.SystemBus(private=True,mainloop=NULL_MAIN_LOOP)
                started=False
                try:
                    scanner=dbus.Interface(scan_bus.get_object('org.bluez',a),ADAPTER)
                    scanner.StartDiscovery(timeout=15);started=True;time.sleep(10)
                finally:
                    try:
                        if started:scanner.StopDiscovery(timeout=15)
                    finally:scan_bus.close()
        elif action in ('pair','connect','disconnect','forget','auto'):
            idle_audio();path,d=device(req.get('mac'))
            if action=='pair':
                if d.get('Paired'):raise ValueError('Already paired. Choose Connect.')
                PAIR_TARGET=path
                try:
                    call(path,DEVICE,'Pair',timeout=90)
                    call(path,PROPS,'Set',DEVICE,'Trusted',dbus.Boolean(True))
                finally:PAIR_TARGET=None;clear_challenge(True)
            elif action=='connect':
                if not d.get('Paired'):raise ValueError('Pair the device first.')
                call(path,DEVICE,'Connect',timeout=30);SUSPENDED.discard(str(d['Address']))
            elif action=='disconnect':
                call(path,DEVICE,'Disconnect');SUSPENDED.add(str(d['Address']))
            elif action=='forget':
                if req.get('confirm') is not True:raise ValueError('Confirmation required.')
                call(str(d['Adapter']),ADAPTER,'RemoveDevice',dbus.ObjectPath(path))
                PREFERENCES['auto']=[m for m in PREFERENCES.get('auto',[]) if m!=str(d['Address'])];save()
            elif action=='auto':
                if not d.get('Paired'):raise ValueError('Pair the device first.')
                entries=set(PREFERENCES.get('auto',[]));mac=str(d['Address'])
                if req.get('on'):entries.add(mac);call(path,PROPS,'Set',DEVICE,'Trusted',dbus.Boolean(True))
                else:entries.discard(mac)
                PREFERENCES['auto']=sorted(entries);SUSPENDED.discard(mac);save()
        elif action=='volume':
            value=req.get('value')
            if type(value) is not int or not 0<=value<=100:raise ValueError('Volume must be 0-100%.')
            st=audio_status();name=req.get('sink')
            if name!=st['sink']:raise ValueError('Output changed. Open Volume again.')
            audio('set-sink-volume',name,str(value)+'%')
        elif action=='transport':
            select_transport(req.get('transport'))
        elif action=='route':
            if req.get('kind') not in ('sink','source'):raise ValueError('Invalid audio route.')
            set_route(req['kind'],req.get('name'))
        elif action=='profile':
            idle_audio();st=audio_status();card=next((c for c in st['cards'] if c['name']==req.get('card')),None)
            if not card or req.get('profile') not in {p['name'] for p in card['profiles']}:raise ValueError('Profile unavailable.')
            audio('set-card-profile',card['name'],req['profile'])
            PREFERENCES.setdefault('profiles',{})[card['name']]=req['profile'];save()
            time.sleep(1)
        else:raise ValueError('Unknown operation.')
        return dict(ok=True,message='Done',status=snapshot())
    finally:LOCK.release()


class Handler(socketserver.StreamRequestHandler):
    def handle(self):
        self.request.settimeout(5)
        try:
            raw=self.rfile.readline(4097)
            if len(raw)>4096:raise ValueError('Invalid request.')
            req=json.loads(raw)
            if not isinstance(req,dict):raise ValueError('Invalid request.')
            result=dispatch(req)
        except dbus.DBusException as e:
            name=e.get_dbus_name().rsplit('.',1)[-1]
            result=dict(ok=False,message={'AuthenticationFailed':'Pairing failed. Try pairing mode again.','AuthenticationRejected':'Pairing was rejected.','AuthenticationCanceled':'Pairing cancelled.','AuthenticationTimeout':'Pairing timed out.','NotReady':'Enable Bluetooth first.','ConnectionAttemptFailed':'Device unavailable. Try again.'}.get(name,'Bluetooth operation failed. Try again.'))
        except ValueError as e:result=dict(ok=False,message=str(e))
        except Exception:result=dict(ok=False,message='Operation failed. Please retry.')
        try:self.wfile.write((json.dumps(result)+'\n').encode())
        except (OSError,ConnectionError):pass

class Server(socketserver.ThreadingUnixStreamServer):
    daemon_threads=True


def maintain():
    # Reconnect only devices explicitly opted in; never switch audio while transmitting.
    while True:
        time.sleep(30)
        if not LOCK.acquire(False):continue
        try:
            idle_audio();st=snapshot()
            if not st['powered']:continue
            for d in st['devices']:
                if d['auto'] and d['paired'] and not d['connected'] and d['mac'] not in SUSPENDED:
                    try:call(device(d['mac'])[0],DEVICE,'Connect',timeout=8)
                    except Exception:pass
            st=audio_status()
            for card in st['cards']:
                preferred=PREFERENCES.get('profiles',{}).get(card['name'])
                if preferred and preferred!=card['active'] and preferred in {p['name'] for p in card['profiles']}:
                    audio('set-card-profile',card['name'],preferred)
            st=audio_status()
            for kind,plural in [('sink','sinks'),('source','sources')]:
                name=PREFERENCES.get(kind)
                if name and name!=st[kind] and name in {n['name'] for n in st[plural]}:set_route(kind,name,False)
        except Exception:pass
        finally:LOCK.release()


def main():
    global PREFERENCES
    try:PREFERENCES=json.loads(PREF.read_text())
    except (OSError,ValueError):PREFERENCES={}
    threads_init()
    DBusGMainLoop(set_as_default=True)
    bus=dbus.SystemBus();agent=Agent(bus,'/org/sqlink/BluetoothAgent')
    manager=dbus.Interface(bus.get_object('org.bluez','/org/bluez'),'org.bluez.AgentManager1')
    manager.RegisterAgent('/org/sqlink/BluetoothAgent','KeyboardDisplay');manager.RequestDefaultAgent('/org/sqlink/BluetoothAgent')
    pathlib.Path(SOCKET).unlink(missing_ok=True)
    server=Server(SOCKET,Handler);os.chown(SOCKET,0,grp.getgrnam('sqlink').gr_gid);os.chmod(SOCKET,0o660)
    threading.Thread(target=server.serve_forever,daemon=True).start()
    threading.Thread(target=maintain,daemon=True).start()
    GLib.MainLoop().run()

if __name__=='__main__':main()
