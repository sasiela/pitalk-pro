"""Bounded, authenticated, transient receive audio for the local web panel."""
import os,pathlib,select,subprocess,threading,time
SLOTS=threading.BoundedSemaphore(4)

def receiving():
 try:
  p=pathlib.Path('/dev/shm/sqlink-radio-state').read_text().split()
  return p[0]==pathlib.Path('/run/svxlink.pid').read_text().strip() and p[2]=='1'
 except (OSError,IndexError):return False

def monitor():
 name=subprocess.check_output(['pactl','get-default-sink'],text=True,timeout=2).strip()
 if not name:raise RuntimeError('No output device')
 return name+'.monitor'

def capture(device):
 return subprocess.Popen(['parec','--raw','--format=s16le','--rate=16000','--channels=1','--latency-msec=50','--client-name=PiTalk web listen','--device='+device],stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,bufsize=0)

def stop(proc):
 if proc:
  if proc.poll() is None:proc.terminate()
  try:proc.wait(timeout=1)
  except subprocess.TimeoutExpired:proc.kill();proc.wait()
  proc.stdout.close()

def stream(handler):
 if not SLOTS.acquire(False):return handler.reply(429,dict(ok=False,message='All listening slots are busy. Try again shortly.'))
 proc=None;started=False
 try:
  device=monitor();proc=capture(device)
  if not select.select([proc.stdout],[],[],3)[0]:raise RuntimeError('Audio unavailable')
  first=os.read(proc.stdout.fileno(),3200)
  if not first:raise RuntimeError('Audio unavailable')
  handler.send_response(200);handler.headers_common();handler.send_header('Content-Type','application/octet-stream');handler.send_header('Connection','close');handler.send_header('X-Audio-Format','s16le;rate=16000;channels=1');handler.end_headers();started=True
  handler.connection.settimeout(3);handler.close_connection=True
  handler.wfile.write(first if receiving() else bytes(len(first)));handler.wfile.flush()
  check=time.monotonic();pending=b''
  while handler.session():
   now=time.monotonic()
   if now-check>1:
    check=now;new=monitor()
    if new!=device:
     stop(proc);proc=None;device=new;proc=capture(device);pending=b''
   if not select.select([proc.stdout],[],[],2)[0]:break
   data=os.read(proc.stdout.fileno(),3200)
   if not data:break
   pending+=data
   size=len(pending)//2*2
   if not size:continue
   chunk=pending[:size];pending=pending[size:]
   handler.wfile.write(chunk if receiving() else bytes(size));handler.wfile.flush()
 except (BrokenPipeError,ConnectionResetError,TimeoutError):pass
 except Exception:
  if not started:handler.reply(503,dict(ok=False,message='Audio output unavailable. Check Audio settings and retry.'))
 finally:
  stop(proc);SLOTS.release()
