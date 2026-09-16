"""Four-button PiTFT Wi-Fi menu; network work stays off the display loop."""
import json
import queue
import socket
import string
import threading
from PIL import Image, ImageDraw, ImageFont
from sqlink import theme
from sqlink.theme import MenuDraw, footer_icons


def request(payload):
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
        sock.settimeout(120)
        sock.connect('/run/sqlink-wifi/control.sock')
        sock.sendall((json.dumps(payload) + '\n').encode())
        with sock.makefile('rb') as stream:
            data = stream.readline(131073)
        if len(data) > 131072:
            raise ValueError()
        return json.loads(data)


class WiFiMenu:
    def __init__(self):
        self.page = 'home'
        self.index = 0
        self.status = {}
        self.networks = []
        self.selected = None
        self.busy = False
        self.message = ''
        self.password = ''
        self.charset = 'abc'
        self.key_index = 0
        self.results = queue.Queue()
        self.font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 15)
        self.small = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 12)
        self.title = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 20)

    def start(self, payload, target):
        if self.busy:
            return
        self.busy = True
        self.message = {'connect': 'Laczenie...', 'set_default': 'Zapisywanie...'}.get(payload['action'], 'Odczyt sieci...')
        def worker():
            try:
                result = request(payload)
            except Exception:
                result = dict(ok=False, message='Brak odpowiedzi uslugi Wi-Fi.')
            finally:
                payload.pop('password', None)
            self.results.put((target, result))
        threading.Thread(target=worker, daemon=True).start()

    def enter(self):
        self.page, self.index = 'home', 0
        self.password = ''
        self.start(dict(action='snapshot'), 'home')

    def poll(self):
        try:
            target, result = self.results.get_nowait()
        except queue.Empty:
            return False
        self.busy = False
        self.message = result.get('message', '')
        if result.get('ok'):
            self.status = result.get('status', self.status)
            self.networks = result.get('networks', self.networks)
            self.page, self.index = target, 0
        else:
            self.page, self.index = 'error', 0
        return True

    def options(self):
        if self.page == 'home':
            return ['Skanuj sieci', 'Zapisane sieci', 'Odswiez status']
        if self.page == 'scan':
            return [r['ssid'] for r in self.networks] or ['Brak sieci - skanuj ponownie']
        if self.page == 'saved':
            return [('★ ' if r.get('default') else '') + r['ssid'] for r in self.status.get('saved', [])] or ['Brak zapisanych sieci']
        if self.page == 'detail':
            if self.selected.get('uuid'):
                return ['Polacz', 'Ustaw jako domyslna', 'Wroc']
            return ['Polacz', 'Wroc']
        return []

    def keys(self):
        chars = {'abc': string.ascii_lowercase, 'ABC': string.ascii_uppercase,
                 '123': string.digits, '#+=': string.punctuation}[self.charset]
        return list(chars) + ['SP', 'DEL', 'abc', 'ABC', '123', '#+=', 'OK']

    def button(self, name):
        if self.busy:
            return False
        if self.page == 'password':
            if name == 'BACK':
                self.password = ''
                self.page, self.index = 'detail', 0
                return False
            keys = self.keys()
            if name in ('UP', 'DOWN'):
                self.key_index = (self.key_index + (1 if name == 'DOWN' else -1)) % len(keys)
            if name == 'ENTER':
                key = keys[self.key_index]
                if key in ('abc', 'ABC', '123', '#+='):
                    self.charset, self.key_index = key, 0
                elif key == 'DEL':
                    self.password = self.password[:-1]
                elif key == 'OK':
                    valid = 8 <= len(self.password) <= 63 or (len(self.password) == 64 and
                            all(c in string.hexdigits for c in self.password))
                    if valid:
                        payload = dict(action='connect', ssid=self.selected['ssid'], password=self.password)
                        self.password = ''
                        self.start(payload, 'home')
                    else:
                        self.message = 'Haslo: 8-63 znaki / 64 hex'
                elif len(self.password) < 64:
                    self.password += ' ' if key == 'SP' else key
                    self.message = ''
            return False
        if name == 'BACK':
            self.password = ''
            if self.page == 'home':
                return True
            self.page, self.index, self.message = 'home', 0, ''
            return False
        if self.page == 'error':
            if name == 'ENTER':
                self.page, self.index = 'home', 0
            return False
        opts = self.options()
        if name in ('UP', 'DOWN') and opts:
            self.index = (self.index + (1 if name == 'DOWN' else -1)) % len(opts)
        if name != 'ENTER':
            return False
        if self.page == 'home':
            if self.index == 0:
                self.start(dict(action='scan'), 'scan')
            elif self.index == 1:
                self.start(dict(action='snapshot'), 'saved')
            else:
                self.start(dict(action='snapshot'), 'home')
        elif self.page == 'scan':
            if not self.networks:
                self.start(dict(action='scan'), 'scan')
            else:
                self.selected = dict(self.networks[self.index])
                profile = next((p for p in self.status.get('saved', [])
                                if p['ssid'] == self.selected['ssid']), None)
                if profile:
                    self.selected.update(uuid=profile['uuid'], default=profile.get('default', False))
                self.page, self.index = 'detail', 0
        elif self.page == 'saved' and self.status.get('saved'):
            self.selected = dict(self.status['saved'][self.index])
            self.page, self.index = 'detail', 0
        elif self.page == 'detail':
            if self.index == 1 and self.selected.get('uuid'):
                self.start(dict(action='set_default', uuid=self.selected['uuid']), 'saved')
            elif self.index == len(self.options()) - 1:
                self.page, self.index = 'home', 0
            elif self.selected.get('uuid'):
                self.start(dict(action='connect', uuid=self.selected['uuid']), 'home')
            elif not self.selected.get('supported', False):
                self.page, self.message = 'error', 'Ta siec wymaga innej konfiguracji.'
            elif self.selected.get('security') in ('', '--'):
                self.start(dict(action='connect', ssid=self.selected['ssid']), 'home')
            else:
                self.page, self.password, self.charset, self.key_index = 'password', '', 'abc', 0
                self.message = ''
        return False

    def render_home(self):
        img = Image.new('RGB', (240, 320), theme.BG)
        d = ImageDraw.Draw(img)
        muted, white, accent = theme.MUTED, theme.TEXT, theme.ACCENT
        def text(x, y, value, font=None, color=white, width=200):
            font = font or self.font
            value = ''.join(c if c.isprintable() else '?' for c in str(value))
            if d.textlength(value, font=font) > width:
                while value and d.textlength(value + '…', font=font) > width:
                    value = value[:-1]
                value += '…'
            d.text((x, y), value, font=font, fill=color)
        text(60, 17, 'Wi-Fi', self.title)
        text(154, 22, 'POŁĄCZENIE', self.small, muted, 76)
        # Status is a non-selectable card; actions begin below it.
        d.rounded_rectangle((10, 47, 229, 165), radius=9, fill=theme.PANEL)
        connected = self.status.get('connected', False)
        state = 'Połączono' if connected else ('Rozłączono' if self.status.get('radio', True) else 'Wi-Fi wyłączone')
        color = '#74e2aa' if connected else '#efc678'
        d.ellipse((21, 61, 27, 67), fill=color)
        text(35, 56, state, self.small, color, 180)
        text(20, 78, self.status.get('ssid') if connected else 'Brak aktywnej sieci', self.font)
        ip = (self.status.get('ip') or '').split('/')[0]
        text(20, 104, 'IP', self.small, muted, 20)
        text(44, 102, ip if connected and ip else '—', self.font, white, 172)
        d.line((20, 130, 218, 130), fill=theme.LINE)
        default = next((p['ssid'] for p in self.status.get('saved', []) if p.get('default')), None)
        text(20, 140, '★ Domyślna: ' + default if default else 'Domyślna: nie wybrano', self.small, muted, 198)
        text(12, 177, 'ZARZĄDZANIE', self.small, muted)
        labels = ['Skanuj sieci', 'Zapisane sieci', 'Odśwież status']
        for i, label in enumerate(labels):
            y = 193 + i * 28
            selected = i == self.index
            if selected:
                d.rounded_rectangle((10, y-2, 229, y+25), radius=5, fill=theme.SELECTED)
                d.rounded_rectangle((10, y+2, 13, y+21), radius=1, fill=accent)
            text(23, y+2, label, self.font, white if selected else muted, 182)
            if selected:
                text(214, y+2, '›', self.font, accent, 10)
        d.line((12, 279, 228, 279), fill=theme.LINE)
        footer_icons(img, right='enter', enabled=not self.busy)
        return img

    def render(self):
        if self.page == 'home' and not self.busy:
            return self.render_home()
        img = Image.new('RGB', (240, 320), theme.BG)
        d = MenuDraw(img)
        def text(x, y, s, font=None, color='white', width=216):
            s = ''.join(c if c.isprintable() else '?' for c in str(s))
            font = font or self.font
            while s and d.textlength(s, font=font) > width:
                s = s[:-2] + '…' if len(s) > 1 else ''
            d.text((x, y), s, font=font, fill=color)
        text(60, 17, 'Wi-Fi', self.title)
        text(128, 22, {'scan': 'Dostępne sieci', 'saved': 'Zapisane sieci', 'detail': 'Wybrana sieć', 'password': 'Hasło sieci', 'error': 'Komunikat'}.get(self.page, 'Połączenie'), self.small, width=100)
        d.line((12, 40, 228, 40), fill='white')
        if self.busy:
            text(12, 90, self.message)
            text(12, 120, 'Prosze czekac...', self.small)
            text(12, 150, 'PTT dziala niezaleznie.', self.small)
        elif self.page == 'password':
            text(12, 47, self.selected['ssid'])
            text(12, 71, '*' * min(len(self.password), 20), width=180)
            text(201, 73, str(len(self.password)), self.small, width=30)
            keys = self.keys()
            # Six columns, with automatic page scrolling for symbols.
            start_row = max(0, self.key_index // 6 - 4)
            for i in range(start_row * 6, min(len(keys), (start_row + 5) * 6)):
                x, y = 9 + (i % 6) * 37, 101 + (i // 6 - start_row) * 29
                if i == self.key_index:
                    d.rounded_rectangle((x, y, x+35, y+26), radius=4, fill=theme.SELECTED, outline=theme.ACCENT)
                text(x+3, y+5, keys[i], self.small,
                     theme.ACCENT if i == self.key_index else 'white', width=31)
            text(12, 250, self.message or 'SP spacja  DEL usun  OK polacz', self.small)
            text(12, 264, 'UP/DOWN znak; ENTER wybiera', self.small)
        elif self.page == 'error':
            words, line, y = self.message.split(), '', 75
            for word in words:
                if d.textlength((line + ' ' + word).strip(), font=self.font) > 210:
                    text(12, y, line)
                    y += 24
                    line = word
                else:
                    line = (line + ' ' + word).strip()
            text(12, y, line)
        else:
            top = 105
            if self.page == 'home':
                text(12, 48, self.status.get('ssid') or 'Brak polaczenia')
                text(12, 74, self.status.get('ip') or 'Brak adresu IP', self.small)
                text(12, 267, self.message, self.small)
            elif self.page == 'detail':
                text(12, 48, ('★ ' if self.selected.get('default') else '') + self.selected['ssid'])
                text(12, 75, ('Zapisany profil' if self.selected.get('uuid') else
                     ('Siec otwarta - bez szyfrowania' if self.selected.get('security') in ('', '--')
                      else self.selected.get('security', ''))), self.small)
            else:
                text(12, 49, 'Wybierz sieć', self.small)
                top = 78
            opts = self.options()
            start = max(0, self.index - 4)
            for i in range(start, min(len(opts), start+5)):
                y = top + (i-start)*36
                if i == self.index:
                    d.rectangle((9, y-3, 231, y+30), outline='white', width=2)
                label = opts[i]
                if self.page == 'scan' and self.networks:
                    row = self.networks[i]
                    text(16, y, label, width=165)
                    text(187, y+2, str(row['signal'])+'%', self.small, width=39)
                    text(16, y+18, ('* ' if row['active'] else '') + (row['security'] or 'Otwarta'), self.small)
                else:
                    text(16, y+3, label, width=205)
        d.line((12, 279, 228, 279), fill='white')
        footer_icons(img, right='enter', enabled=not self.busy)
        return img
