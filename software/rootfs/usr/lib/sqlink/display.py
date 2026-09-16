"""Persistent Display settings and four-button editor."""
import json
import os
import pathlib
from PIL import Image, ImageDraw, ImageFont
from . import theme

PATH = pathlib.Path('/var/lib/sqlink-display/settings.json')
DEFAULTS = dict(brightness=100, color_scheme='Ocean', idle_timeout=30)
TIMEOUTS = [10, 20, 30, 60, 120, 300, 0]


class Settings:
    def __init__(self, path=PATH):
        self.path = pathlib.Path(path)
        self.values = dict(DEFAULTS)
        try:
            data = json.loads(self.path.read_text())
            if type(data.get('brightness')) is int and 10 <= data['brightness'] <= 100:
                self.values['brightness'] = data['brightness']
            if data.get('color_scheme') in theme.SCHEMES:
                self.values['color_scheme'] = data['color_scheme']
            if type(data.get('idle_timeout')) is int and data['idle_timeout'] in TIMEOUTS:
                self.values['idle_timeout'] = data['idle_timeout']
        except (OSError, ValueError, TypeError, AttributeError):
            pass
        self.apply()

    def apply(self):
        theme.set_scheme(self.values['color_scheme'])

    def save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_suffix('.tmp')
        try:
            with open(tmp, 'w') as out:
                os.chmod(tmp, 0o600)
                json.dump(self.values, out)
                out.flush()
                os.fsync(out.fileno())
            os.replace(tmp, self.path)
        finally:
            tmp.unlink(missing_ok=True)

    def dim(self, image):
        value = self.values['brightness']
        if value == 100:
            return image
        lut = [round(i * value / 100) for i in range(256)]
        return image.point(lut * 3)


class DisplayMenu:
    def __init__(self, settings):
        self.settings = settings
        self.index = 0
        self.editing = False
        self.original = None
        self.message = ''
        self.font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 15)
        self.small = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 12)
        self.title = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 20)

    def enter(self):
        self.cancel()
        self.index = 0
        self.message = ''

    def cancel(self):
        if self.editing:
            self.settings.values = self.original
            self.settings.apply()
        self.editing = False
        self.original = None

    def button(self, name):
        if name == 'BACK':
            if self.editing:
                self.cancel()
                self.message = 'Changes cancelled'
                return False
            return True
        if name == 'ENTER':
            if not self.editing:
                self.original = dict(self.settings.values)
                self.editing = True
                self.message = ''
            else:
                try:
                    self.settings.save()
                except OSError:
                    self.message = 'Could not save. Try again.'
                    return False
                self.editing = False
                self.original = None
                self.message = 'Settings saved'
            return False
        if name in ('UP', 'DOWN'):
            step = 1 if name == 'DOWN' else -1
            if not self.editing:
                self.index = (self.index + step) % 3
            else:
                key = ['brightness', 'color_scheme', 'idle_timeout'][self.index]
                value = self.settings.values[key]
                if key == 'brightness':
                    self.settings.values[key] = min(100, max(10, value - step * 10))
                else:
                    choices = list(theme.SCHEMES) if key == 'color_scheme' else TIMEOUTS
                    self.settings.values[key] = choices[(choices.index(value) + step) % len(choices)]
                self.settings.apply()
            self.message = ''
        return False

    def render(self):
        img = Image.new('RGB', (240, 320), theme.BG)
        d = ImageDraw.Draw(img)
        d.text((144, 29), 'Display', font=self.title, fill=theme.TEXT, anchor='mm')
        d.line((12, 46, 228, 46), fill=theme.LINE)
        v = self.settings.values
        labels = [('Brightness', str(v['brightness'])+'%'), ('Color scheme', v['color_scheme']),
                  ('Idle timeout', str(v['idle_timeout'])+' sec' if v['idle_timeout'] else 'Never')]
        for i, (label, value) in enumerate(labels):
            y = 62 + i * 54
            if i == self.index:
                d.rounded_rectangle((10, y-4, 229, y+43), radius=6, fill=theme.SELECTED,
                                    outline=theme.ACCENT if self.editing else None)
                d.rounded_rectangle((10,y,13,y+39),radius=1,fill=theme.ACCENT)
            d.text((23,y),label,font=self.font,fill=theme.TEXT)
            d.text((23,y+23),value,font=self.small,fill=theme.ACCENT if i==self.index else theme.MUTED)
        hint = ['Image dimming (not backlight)', 'Preview colors before saving', 'Return to the home screen'][self.index]
        d.text((12,226),hint,font=self.small,fill=theme.MUTED)
        d.text((12,247),self.message or ('UP/DOWN adjust; check to save' if self.editing else 'Select an option to edit'),font=self.small,fill=theme.MUTED)
        d.line((12,273,228,273),fill=theme.LINE)
        theme.footer_icons(img,right='enter')
        return img
