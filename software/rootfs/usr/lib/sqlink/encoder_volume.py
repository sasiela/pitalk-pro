"""Non-blocking home-screen volume, using the existing audio helper."""
import queue
import threading
from .bluetooth_ui import request


def adjust_volume(send, delta):
    result = send({'action': 'status'})
    if not result.get('ok'):
        raise RuntimeError('Audio unavailable')
    audio = result.get('status', {}).get('audio', {})
    sink = next((s for s in audio.get('sinks', [])
                 if s['name'] == audio.get('sink')), None)
    if sink is None:
        raise RuntimeError('No audio output')
    value = max(0, min(100, int(sink.get('volume', 0)) + delta))
    result = send({'action': 'volume', 'sink': sink['name'], 'value': value})
    if not result.get('ok'):
        raise RuntimeError('Could not set volume')
    return value


class HomeVolume:
    def __init__(self):
        self.pending = 0
        self.running = False
        self.results = queue.Queue()

    def turn(self, action):
        self.pending += 5 if action == 'DOWN' else -5
        self.start()

    def start(self):
        if self.running or not self.pending:
            return
        delta, self.pending = self.pending, 0
        self.running = True
        def worker():
            try:
                value = adjust_volume(request, delta)
                self.results.put((True, 'Volume: %d%%' % value))
            except Exception as exc:
                self.results.put((False, str(exc) or 'Audio unavailable'))
        threading.Thread(target=worker, daemon=True).start()

    def poll(self):
        try:
            ok, message = self.results.get_nowait()
        except queue.Empty:
            return None
        self.running = False
        if not ok:
            self.pending = 0
        self.start()
        return message
