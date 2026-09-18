"""Bounded local audio diagnostics. Never operates PTT or stores microphone audio."""
import array
import json
import math
import pathlib
import select
import secrets
import subprocess
import sys
import tempfile
import threading
import time

LOCK = threading.Lock()
JOB = None

def radio_idle():
    try:
        if pathlib.Path('/sys/class/gpio/gpio536/value').read_text().strip() != '1':
            return False
        parts = pathlib.Path('/dev/shm/sqlink-radio-state').read_text().split()
        return (int(parts[0]) == int(pathlib.Path('/run/svxlink.pid').read_text())
                and int(parts[2]) == 0)
    except (OSError, ValueError, IndexError):
        return False

def pactl(*args):
    return subprocess.check_output(['pactl', *args], text=True, timeout=2,
                                   stderr=subprocess.DEVNULL).strip()

def device(kind):
    name = pactl('get-default-' + kind)
    devices = json.loads(pactl('-f', 'json', 'list', kind + 's'))
    d = next((d for d in devices if d['name'] == name), None)
    if not d or name.endswith('.monitor') or name == 'auto_null':
        raise ValueError('No physical audio device available. Check Audio routing.')
    if d.get('mute'):
        raise ValueError('Selected audio device is muted. Unmute it before testing.')
    return name, d.get('description') or name

def levels(data):
    samples = array.array('h', data[:len(data)//2*2])
    if sys.byteorder != 'little':
        samples.byteswap()
    if not samples:
        return -60.0, 0.0
    peak = max(abs(s) for s in samples) / 32768
    rms = math.sqrt(sum(s*s for s in samples) / len(samples)) / 32768
    return round(max(-60, 20 * math.log10(max(rms, 1e-9))), 1), peak

def snapshot(owner):
    with LOCK:
        if JOB is None:
            return dict(active=False, message='Ready to test.')
        if JOB['owner'] != owner:
            return dict(active=JOB['active'], foreign=True,
                        message='Audio test in use by another session.' if JOB['active'] else 'Ready to test.')
        return {k: v for k, v in JOB.items() if k not in ('owner', 'cancel')}

def stop(owner, job_id=None):
    with LOCK:
        if JOB and JOB['owner'] == owner and (job_id is None or JOB['id'] == job_id):
            JOB['cancel'].set()

def start(owner, mode):
    global JOB
    if mode not in ('output', 'microphone'):
        raise ValueError('Choose an output or microphone test.')
    if not radio_idle():
        raise ValueError('Wait until RX and PTT are idle before testing audio.')
    with LOCK:
        if JOB and JOB['active']:
            raise ValueError('An audio test is already running.')
        job = dict(id=secrets.token_hex(8), owner=owner, mode=mode, active=True,
                   cancel=threading.Event(), db=-60, peak=0, seconds=0,
                   message='Preparing audio device…', device='')
        JOB = job
        threading.Thread(target=worker, args=(job,), daemon=True).start()
        return {k: v for k, v in job.items() if k not in ('owner', 'cancel')}

def update(job, **values):
    with LOCK:
        job.update(values)

def worker(job):
    process = None
    tone = None
    message = 'Test stopped.'
    try:
        kind = 'sink' if job['mode'] == 'output' else 'source'
        name, label = device(kind)
        update(job, device=label)
        if job['cancel'].is_set():
            return
        if not radio_idle():
            raise ValueError('Test stopped: radio activity detected.')
        args = ['--raw', '--format=s16le', '--rate=16000', '--channels=1',
                '--latency-msec=50', '--client-name=PiTalk audio test', '--device='+name]
        if kind == 'sink':
            # Generated reference signal only; no microphone data ever reaches a file.
            samples = array.array('h', (int(11000 * math.sin(2*math.pi*660*i/16000)
                * min(1, i/320, (32000-i)/320)) for i in range(32000)))
            if sys.byteorder != 'little':
                samples.byteswap()
            tone = tempfile.TemporaryFile()
            tone.write(samples.tobytes()); tone.seek(0)
            process = subprocess.Popen(['paplay', '--volume=32768', *args], stdin=tone,
                                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            update(job, message='Playing a two-second tone on the device…')
        else:
            process = subprocess.Popen(['parec', *args], stdout=subprocess.PIPE,
                                       stderr=subprocess.DEVNULL, bufsize=0)
            update(job, message='Speak into the device microphone. Do not press PTT.')
        began = last_data = checked = time.monotonic()
        while True:
            now = time.monotonic()
            if job['cancel'].is_set():
                break
            if not radio_idle():
                message = 'Test stopped: radio activity detected.'; break
            if now - checked >= 1:
                if pactl('get-default-'+kind) != name:
                    message = 'Audio routing changed. Start a new test.'; break
                checked = now
            update(job, seconds=round(now-began, 1))
            if kind == 'sink':
                code = process.poll()
                if code is not None:
                    message = ('Tone finished. Did you hear it on the device?' if code == 0
                               else 'Playback failed. Check the selected output.'); break
                if now-began > 4:
                    message = 'Output test timed out. Check the audio device.'; break
                job['cancel'].wait(.05)
            else:
                if now-began >= 8:
                    message = ('Microphone test finished: signal detected.' if job['peak'] > .01
                               else 'Very low or no microphone signal. Check input and microphone gain.'); break
                if process.poll() is not None or now-last_data > 2:
                    message = 'Microphone unavailable. Check input routing and Bluetooth profile.'; break
                if select.select([process.stdout], [], [], .1)[0]:
                    data = process.stdout.read(3200)
                    if not data:
                        message = 'Microphone stream ended.'; break
                    last_data = time.monotonic()
                    db, peak = levels(data)
                    update(job, db=db, peak=max(job['peak'], peak))
        update(job, db=-60)
    except ValueError as exc:
        message = str(exc)
    except Exception:
        message = 'Audio test failed. Check the selected device and try again.'
    finally:
        if process is not None:
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=.5)
                except subprocess.TimeoutExpired:
                    process.kill(); process.wait(timeout=1)
            if process.stdout:
                process.stdout.close()
        if tone:
            tone.close()
        update(job, active=False, message=message)
