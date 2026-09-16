"""Live radio state and transient audio peak meter. No audio is saved."""
import pathlib,subprocess,threading,time,select,array,math

class RadioStatus:
    def __init__(self):
        self.talker='';self.mode='IDLE';self.level=0.0;self.available=False
        threading.Thread(target=self._meter,daemon=True).start()
    def state(self,online,ptt):
        tg=None;rx=False;self.talker=""
        try:
            fields=pathlib.Path('/dev/shm/sqlink-radio-state').read_text().split(maxsplit=3)
            pid,tg,rx=map(int,fields[:3])
            if len(fields)>3:self.talker=fields[3].strip()
            if pid!=int(pathlib.Path('/run/svxlink.pid').read_text()):tg=None;rx=False
        except (OSError,ValueError):pass
        mode='TX' if ptt else 'OFFLINE' if not online else 'RX' if rx else 'MONITOR' if tg==0 else 'IDLE'
        if mode != "RX":self.talker=""
        self.mode=mode
        return mode,tg,self.level if mode in ('TX','RX') else 0,self.available
    def _meter(self):
        proc=None;key=None;last_check=0;retry=0
        while True:
            try:
                mode=self.mode
                if mode not in ('TX','RX'):
                    if proc:proc.terminate();proc.wait(timeout=1);proc=None
                    self.level=0;self.available=False;key=None;time.sleep(.05);continue
                now=time.monotonic()
                if now-last_check>1 or not proc:
                    last_check=now
                    cmd='get-default-source' if mode=='TX' else 'get-default-sink'
                    dev=subprocess.check_output(['pactl',cmd],text=True,timeout=2).strip()
                    if mode=='RX':dev+='.monitor'
                    new=(mode,dev)
                    if new!=key or (proc and proc.poll() is not None):
                        if proc:proc.terminate();proc.wait(timeout=1);proc=None
                        key=new
                    if not proc:
                        if now<retry:time.sleep(.1);continue
                        proc=subprocess.Popen(['parec','--raw','--format=s16le','--rate=16000','--channels=1','--latency-msec=50','--client-name=SQLink level meter','--device='+dev],stdout=subprocess.PIPE,stderr=subprocess.DEVNULL)
                        retry=now+2
                if select.select([proc.stdout],[],[],.1)[0]:
                    data=proc.stdout.read(1600)
                    if not data:
                        proc.wait(timeout=1);proc=None;self.available=False;self.level=0;continue
                    samples=array.array('h',data[:len(data)//2*2])
                    peak=max(map(abs,samples),default=0)/32768
                    db=20*math.log10(max(peak,1e-6))
                    self.level=max(max(0,min(1,(db+60)/60)),self.level*.75)
                    self.available=True
            except Exception:
                if proc:
                    try:proc.kill();proc.wait(timeout=1)
                    except Exception:pass
                proc=None;key=None;self.available=False;self.level=0;time.sleep(1)
