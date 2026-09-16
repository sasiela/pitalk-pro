"""Shared PiTFT palette and drawing style."""
from PIL import ImageDraw

BG = '#080d14'
PANEL = '#142131'
TEXT = '#f4f7fa'
MUTED = '#9baebe'
ACCENT = '#5dd6ef'
SELECTED = '#173b4b'
LINE = '#2a3b4b'


SCHEMES = {
    'Ocean': ('#080d14','#142131','#f4f7fa','#9baebe','#5dd6ef','#173b4b','#2a3b4b'),
    'Forest': ('#09120e','#14281d','#f1f8f3','#a0b9aa','#74e2aa','#1d4430','#2c4938'),
    'Amber': ('#151008','#2c2112','#fff6e8','#c1af95','#ffc568','#4b3518','#51402a'),
    'Violet': ('#100c18','#231b32','#f7f1ff','#b5a8c7','#c5a0ff','#3e2a57','#443653'),
    'Mono': ('#101010','#222222','#ffffff','#b5b5b5','#ffffff','#393939','#555555'),
}

def set_scheme(name):
    global BG, PANEL, TEXT, MUTED, ACCENT, SELECTED, LINE
    BG, PANEL, TEXT, MUTED, ACCENT, SELECTED, LINE = SCHEMES[name]


class MenuDraw:
    def __init__(self, image, panel=False):
        self.raw = ImageDraw.Draw(image)
        self.selected = None
        self.width = image.width
        if panel:
            self.raw.rounded_rectangle((8, 53, image.width-9, 267), radius=8, fill=PANEL)

    def __getattr__(self, name):
        return getattr(self.raw, name)

    def line(self, xy, fill=None, **kwargs):
        return self.raw.line(xy, fill=LINE if fill == 'white' else fill, **kwargs)

    def rectangle(self, xy, fill=None, outline=None, **kwargs):
        if outline == 'white':
            self.selected = xy
            x1, y1, x2, y2 = xy
            self.raw.rounded_rectangle(xy, radius=5, fill=SELECTED)
            self.raw.rounded_rectangle((x1, y1+3, x1+3, y2-3), radius=1, fill=ACCENT)
            return
        return self.raw.rectangle(xy, fill=fill, outline=outline, **kwargs)

    def text(self, xy, text, fill=None, **kwargs):
        x, y = xy
        text = str(text)
        if text.startswith('> '):
            text = text[2:]
        if fill == 'white':
            fill = TEXT
            if y >= 286 or text.endswith(':'):
                fill = MUTED
            elif text in ('ONLINE', 'Połączono'):
                fill = '#74e2aa'
            elif text == 'OFFLINE':
                fill = '#efc678'
            elif text == 'TX':
                fill = ACCENT
            elif 48 < y < 284 and kwargs.get('font') and getattr(kwargs['font'], 'size', 15) <= 12:
                fill = MUTED
        anchor = kwargs.get('anchor', 'la')
        font = kwargs.get('font')
        if y == 29 and anchor == 'mm':
            xy = (144, y)
            if font and self.raw.textlength(text, font=font) > 164:
                while text and self.raw.textlength(text+'…', font=font) > 164:
                    text = text[:-1]
                text += '…'
        if font and anchor.startswith(('l', 'r')):
            width = self.width-x-10 if anchor.startswith('l') else x-10
            if self.raw.textlength(text, font=font) > width:
                while text and self.raw.textlength(text+'…', font=font) > width:
                    text = text[:-1]
                text += '…'
        return self.raw.text(xy, text, fill=fill, **kwargs)


def footer_icons(image, left='back', right=None, enabled=True):
    """Pixel-drawn navigation symbols, independent of font glyph support."""
    d = ImageDraw.Draw(image)
    color = ACCENT if enabled else LINE
    for x, kind in ((12, left), (12, right)):
        if not kind:
            continue
        y = 12 if kind == "back" else image.height-40
        d.rounded_rectangle((x, y, x+36, y+27), radius=6, outline=color, width=2)
        if kind == 'menu':
            for dy in (8, 14, 20):
                d.line((x+10, y+dy, x+26, y+dy), fill=color, width=2)
        elif kind == 'back':
            d.line((x+26, y+14, x+10, y+14), fill=color, width=2)
            d.line((x+16, y+8, x+10, y+14, x+16, y+20), fill=color, width=2)
        elif kind == 'enter':
            d.line((x+10, y+14, x+16, y+20, x+27, y+8), fill=color, width=3)
