#!/usr/bin/env python3

import os
import re
import time
import subprocess
import json
import urllib.request
from datetime import datetime

import lgpio
from PIL import Image, ImageDraw, ImageFont
from sqlink import theme
from sqlink.theme import MenuDraw, footer_icons
from sqlink.display import Settings, DisplayMenu
display_settings = Settings()
display_menu = DisplayMenu(display_settings)
from sqlink.restart_ui import RestartMenu
restart_menu = RestartMenu()
from sqlink.bluetooth_ui import BluetoothMenu
bluetooth_menu = BluetoothMenu()
from sqlink.audio_ui import AudioMenu
audio_menu = AudioMenu()
from sqlink import profile_state
from sqlink.user_ui import UserMenu
user_menu = UserMenu()

import sys
sys.path.insert(0, "/usr/lib")

from sqlink.controller import SQLinkController

controller = SQLinkController()

from sqlink.wifi_ui import WiFiMenu
wifi_menu = WiFiMenu()

FB = "/dev/fb0"
WIDTH = 240
HEIGHT = 320

SVXCONF = "/etc/svxlink/svxlink.conf"
SVXLOG = "/var/log/svxlink"

BUTTONS = {
    17: "BACK",
    22: "UP",
    23: "DOWN",
    27: "ENTER",
}

MAIN_MENU = [
    "SQLink",
    "Audio",
    "User",
    "Bluetooth",
    "WiFi",
    "Display",
    "Restart",
]

SQLINK_MENU = [
    "Network",
    "Active TG",
    "Last QSO",
    "Stations",
    "Node Info",
    "Talk Groups",
]

FALLBACK_TG_LIST = [
    ("260", "Polska"),
    ("2600", "Ogólnopolska"),
    ("26077", "SQLink"),
    ("260073", "Akcje Dyplomowe"),
    ("999", "Echo / Test"),
    ("27252", "Ireland"),
    ("3109312", "Chicago"),
]

TG_NAMES = {
    "260": "Polska",
    "2600": "Ogólnopolska",
    "26077": "SQLink",
    "260073": "Akcje Dyplomowe",
    "999": "Echo / Test",
    "27252": "Ireland",
    "3109312": "Chicago",
}

TG_LIST = list(FALLBACK_TG_LIST)

TG_API_URL = "https://sqlink.pl/tg_names.json"
TG_REFRESH_INTERVAL = 600
last_tg_refresh = 0.0


def font(size, bold=False):
    path = (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        if bold
        else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    )
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()



FONT_TITLE = font(27, True)
FONT_CALL = font(25, True)
FONT_TG = font(23, True)
FONT_MED = font(18, True)
FONT_SMALL = font(15)
FONT_TINY = font(12)
FONT_MENU = font(20, True)
FONT_MENU_SMALL = font(17)


def read_callsign():
    try:
        section = None
        with open(SVXCONF, "r", errors="ignore") as f:
            for raw in f:
                line = raw.strip()

                if line.startswith("[") and line.endswith("]"):
                    section = line
                    continue

                if (
                    section == "[SimplexLogic]"
                    and line.startswith("CALLSIGN=")
                ):
                    return line.split("=", 1)[1].strip().strip('"')
    except Exception:
        pass

    return "SQLink"



def read_recent_log():
    try:
        with open(SVXLOG, "rb") as f:
            f.seek(0, os.SEEK_END)
            size = f.tell()
            f.seek(max(0, size - 65536))
            return f.read().decode("utf-8", errors="ignore")
    except Exception:
        return ""



def get_active_tg(log):
    patterns = [
        r"Selecting TG #(\d+)",
        r"Talker start on TG #(\d+):",
    ]

    matches = []

    for pattern in patterns:
        for m in re.finditer(pattern, log):
            matches.append((m.start(), m.group(1)))

    if not matches:
        return "---"

    matches.sort(key=lambda x: x[0])
    return matches[-1][1]




def get_tg_name(tg):
    if not tg or tg == "---":
        return ""

    for item_tg, item_name in TG_LIST:
        if str(item_tg) == str(tg):
            return str(item_name)

    return ""



def reflector_connected(log):
    auth = log.rfind("Authentication OK")
    disc1 = log.rfind("Disconnected from")
    disc2 = log.rfind("Heartbeat timeout")

    return auth >= 0 and auth > max(disc1, disc2)



def wifi_info():
    try:
        result = subprocess.run(
            [
                "nmcli",
                "-t",
                "-f",
                "DEVICE,STATE,CONNECTION",
                "device",
            ],
            capture_output=True,
            text=True,
            timeout=2,
        )

        ssid = None

        for line in result.stdout.splitlines():
            parts = line.split(":", 2)

            if len(parts) == 3:
                dev, state, connection = parts

                if dev == "wlan0" and state == "connected":
                    ssid = connection
                    break

        ip = subprocess.run(
            ["hostname", "-I"],
            capture_output=True,
            text=True,
            timeout=2,
        ).stdout.strip().split()

        ipaddr = ip[0] if ip else "---"

        return ssid or "WiFi OFF", ipaddr

    except Exception:
        return "WiFi ?", "---"




def extract_tgs(obj):
    found = set()

    def add_tg(value):
        if value is None:
            return

        text = str(value).strip()

        if text.isdigit():
            num = int(text)

            # Ignore TG0 / empty state.
            if num > 0:
                found.add(str(num))

    def walk(x, parent_key=""):

        if isinstance(x, dict):

            for key, value in x.items():

                key_l = str(key).lower()

                # Single TG-valued fields
                if key_l in (
                    "tg",
                    "talkgroup",
                    "talk_group",
                    "talkgroupid",
                    "talk_group_id",
                    "defaulttg",
                    "default_tg",
                    "localtg",
                    "remotetg",
                ):
                    add_tg(value)

                # Lists of monitored TGs
                elif key_l in (
                    "monitoredtgs",
                    "monitored_tgs",
                    "talkgroups",
                    "talk_groups",
                ):
                    if isinstance(value, list):
                        for item in value:
                            add_tg(item)

                walk(value, key_l)

        elif isinstance(x, list):

            for item in x:
                walk(item, parent_key)

        elif isinstance(x, str):

            # Also catch human-readable TG references
            for m in re.finditer(
                r'(?i)(?:TG|talkgroup)[^0-9]{0,6}([0-9]{2,8})',
                x
            ):
                add_tg(m.group(1))

    walk(obj)

    return found


def load_tg_list():
    global last_tg_refresh

    if profile_state.current().get("directory") != "sqlink":
        last_tg_refresh = time.monotonic()
        return [(str(g["id"]),g["name"]) for g in profile_state.local_groups()] or [("0", "Monitor")]

    try:
        data = controller.talkgroups()

        result = []

        for item in data:
            tg = str(item.get("id", "")).strip()
            name = str(item.get("name", "")).strip()

            if not tg.isdigit():
                continue

            if not name:
                name = "TG " + tg

            result.append((tg, name))

        if result:
            last_tg_refresh = time.monotonic()

            print(
                "TG LIST: controller:",
                len(result),
                "TG",
                flush=True,
            )

            return result

    except Exception as e:
        print(
            "TG CONTROLLER ERROR:",
            e,
            flush=True,
        )

    last_tg_refresh = time.monotonic()

    return list(FALLBACK_TG_LIST) if profile_state.current().get("directory")=="sqlink" else [(str(g["id"]),g["name"]) for g in profile_state.local_groups()]




def refresh_tg_list_if_needed():
    global TG_LIST
    global tg_index
    global last_tg_refresh

    if profile_state.current().get("directory") != "sqlink":
        last_tg_refresh = time.monotonic()
        return [(str(g["id"]),g["name"]) for g in profile_state.local_groups()] or [("0", "Monitor")]

    now = time.monotonic()

    if (
        not TG_LIST
        or last_tg_refresh == 0
        or (now - last_tg_refresh) >= TG_REFRESH_INTERVAL
    ):
        old_selected = None

        if TG_LIST and 0 <= tg_index < len(TG_LIST):
            old_selected = TG_LIST[tg_index][0]

        new_list = load_tg_list()

        if new_list:
            TG_LIST = new_list

            if old_selected:
                for i, item in enumerate(TG_LIST):
                    if item[0] == old_selected:
                        tg_index = i
                        break
                else:
                    tg_index = 0
            else:
                tg_index = 0


from PIL import ImageChops

def framebuffer_bytes(img):
    # Build RGB565 in Pillow's native loops, then interleave low/high bytes.
    r, g, b = img.split()
    high = ImageChops.add(r.point(lambda v: v & 248), g.point(lambda v: v >> 5))
    low = ImageChops.add(g.point(lambda v: (v & 28) << 3), b.point(lambda v: v >> 3))
    return Image.merge("LA", (low, high)).tobytes()

def write_fb(img):
    data = framebuffer_bytes(display_settings.dim(img))
    with open(FB, "wb", buffering=0) as fb:
        fb.write(data)


menu_mode = False
submenu = None
menu_index = 0
tg_index = 0

station_index = 0
station_selected = None
station_list = []

message = ""
message_until = 0.0


def set_message(text, seconds=1.5):
    global message, message_until
    message = text
    message_until = time.monotonic() + seconds



from sqlink.radio_status import RadioStatus
radio_status = RadioStatus()
_main_state = {}
_main_state_time = 0

def draw_main():
    global _main_state, _main_state_time
    try:
        if time.monotonic() - _main_state_time >= 1:
            _main_state = controller.main_status()
            _main_state_time = time.monotonic()
        state = _main_state
    except Exception as e:
        print("CONTROLLER STATUS ERROR:", e, flush=True)
        state = {}

    callsign = state.get("callsign", "SQLink")

    reflector = state.get("reflector", {})

    tg = reflector.get("active_tg") or "---"
    tg_name = reflector.get("active_tg_name") or ""
    connected = bool(reflector.get("connected"))

    radio_mode, radio_tg, audio_level, meter_ready = radio_status.state(connected, bool(state.get("ptt")))
    if radio_tg == 0:
        tg = "---"
        tg_name = ""
    now = datetime.now()

    img = Image.new("RGB", (WIDTH, HEIGHT), theme.BG)
    d = MenuDraw(img)

    # Callsign; the active profile is displayed beside the clock.
    d.text(
        (WIDTH // 2, 36),
        callsign,
        font=FONT_CALL,
        fill="white",
        anchor="mm",
    )

    d.line(
        (12, 58, WIDTH - 12, 58),
        fill="white",
        width=1,
    )

    # Active TG.
    d.text(
        (WIDTH // 2, 90),
        "TG " + str(tg),
        font=FONT_TG,
        fill="white",
        anchor="mm",
    )

    if tg_name:
        d.text(
            (WIDTH // 2, 115),
            str(tg_name)[:30],
            font=FONT_SMALL,
            fill="white",
            anchor="mm",
        )

    if radio_mode == "RX" and radio_status.talker:
        talker = radio_status.talker
        while d.textlength(talker, font=FONT_TG) > WIDTH - 24:
            talker = talker[:-1]
        d.text((WIDTH // 2, (115 + 190) / 2), talker, font=FONT_TG,
               fill="#3B82F6", anchor="mm")

    # Reflector state.
    d.text(
        (WIDTH // 2, 190),
        "ONLINE" if connected else "OFFLINE",
        font=FONT_MED,
        fill="#22C55E" if connected else "#EF4444",
        anchor="mm",
    )

    # Reserve area for future RX/TX/talker indicator.
    ptt = bool(state.get("ptt"))

    d.text(
        (WIDTH // 2, 226),
        radio_mode,
        font=FONT_MED,
        fill="white",
        anchor="mm",
    )

    if radio_mode in ("RX", "TX"):
        meter = ImageDraw.Draw(img)
        meter.rounded_rectangle((25,247,215,257),radius=4,fill=theme.PANEL)
        if meter_ready and audio_level > 0:
            color = "#EF4444" if audio_level > .95 else theme.ACCENT
            meter.rounded_rectangle((25,247,25+190*audio_level,257),radius=4,fill=color)
        if not meter_ready:
            meter.text((WIDTH//2,251),"Audio level unavailable",font=FONT_SMALL,fill=theme.MUTED,anchor="mm")

    d.line(
        (12, 268, WIDTH - 12, 268),
        fill="white",
        width=1,
    )

    if message and time.monotonic() < message_until:
        d.text(
            (WIDTH // 2, 292),
            message,
            font=FONT_SMALL,
            fill="white",
            anchor="mm",
        )
    else:

        clock_text = now.strftime("%H:%M:%S")
        # Keep clear of both the menu icon and the right-aligned clock.
        profile_name = str(profile_state.current().get("name", ""))
        profile_x = 58
        available = max(0, WIDTH - 12 - d.textlength(clock_text, font=FONT_SMALL) - 8 - profile_x)
        if d.textlength(profile_name, font=FONT_TINY) > available:
            while profile_name and d.textlength(profile_name + "…", font=FONT_TINY) > available:
                profile_name = profile_name[:-1]
            profile_name = profile_name + "…" if profile_name else ""
        d.text((profile_x, 288), profile_name, font=FONT_TINY, fill=theme.ACCENT, anchor="la")
        d.text(
            (WIDTH - 12, 286),
            clock_text,
            font=FONT_SMALL,
            fill="white",
            anchor="ra",
        )

    footer_icons(img, left='menu', right=None)
    write_fb(img)




def draw_menu():
    img = Image.new("RGB", (WIDTH, HEIGHT), theme.BG)
    d = MenuDraw(img)

    d.text(
        (WIDTH // 2, 29),
        "MAIN MENU",
        font=FONT_MENU,
        fill="white",
        anchor="mm",
    )

    d.line((12, 46, WIDTH - 12, 46), fill="white", width=1)

    top = 59
    row_h = 35

    start = max(0, menu_index - 5)
    for i in range(start, min(len(MAIN_MENU), start + 6)):
        item = MAIN_MENU[i]
        y = top + (i - start) * row_h

        if i == menu_index:
            d.rectangle(
                (12, y - 6, WIDTH - 12, y + 26),
                outline="white",
                width=2,
            )

            d.text(
                (24, y + 9),
                "> " + item,
                font=FONT_MENU_SMALL,
                fill="white",
                anchor="lm",
            )
        else:
            d.text(
                (24, y + 9),
                item,
                font=FONT_MENU_SMALL,
                fill="white",
                anchor="lm",
            )

    d.line((12, 273, WIDTH - 12, 273), fill="white", width=1)




    footer_icons(img, left='back', right='enter')
    write_fb(img)






def select_tg(tg):
    try:
        command = controller.select_tg(tg)

        print(
            "TG COMMAND:",
            command,
            flush=True,
        )

        return True

    except Exception as e:
        print(
            "TG ERROR:",
            e,
            flush=True,
        )

        return False





def draw_network():

    try:
        data = controller.network_page()

    except Exception as e:
        print(
            "NETWORK PAGE ERROR:",
            e,
            flush=True,
        )
        data = {}

    img = Image.new(
        "RGB",
        (WIDTH, HEIGHT),
        theme.BG,
    )

    d = MenuDraw(img, panel=True)

    d.text(
        (WIDTH // 2, 29),
        "Network",
        font=FONT_MENU,
        fill="white",
        anchor="mm",
    )

    d.line(
        (12, 44, WIDTH - 12, 44),
        fill="white",
        width=1,
    )

    rows = [
        (
            "Server",
            str(
                data.get(
                    "server",
                    profile_state.current().get("host", ""),
                )
            ),
        ),
        (
            "Status",
            "ONLINE"
            if data.get("connected")
            else "OFFLINE",
        ),
        (
            "Stations",
            str(
                data.get(
                    "stations_count",
                    "---",
                )
            ),
        ),
        (
            "Uptime",
            str(
                data.get(
                    "uptime",
                    "---",
                )
            ),
        ),
    ]

    y = 75

    for label, value in rows:

        d.text(
            (14, y),
            label + ":",
            font=FONT_SMALL,
            fill="white",
        )

        d.text(
            (94, y),
            value[:17],
            font=FONT_SMALL,
            fill="white",
        )

        y += 43

    d.line(
        (12, 275, WIDTH - 12, 275),
        fill="white",
        width=1,
    )

    pass  # Footer button captions removed.

    footer_icons(img, left='back', right=None)
    write_fb(img)





def draw_active_tg():

    try:
        active = controller.active_talkgroups()

    except Exception as e:
        print(
            "ACTIVE TG PAGE ERROR:",
            e,
            flush=True,
        )
        active = []

    img = Image.new(
        "RGB",
        (WIDTH, HEIGHT),
        theme.BG,
    )

    d = MenuDraw(img)

    d.text(
        (WIDTH // 2, 29),
        "Active TG",
        font=FONT_MENU,
        fill="white",
        anchor="mm",
    )

    d.line(
        (12, 44, WIDTH - 12, 44),
        fill="white",
        width=1,
    )

    y = 58

    if not active:

        d.text(
            (WIDTH // 2, 140),
            "No active TG",
            font=FONT_MED,
            fill="white",
            anchor="mm",
        )

    else:

        for item in active[:6]:

            tg = str(
                item.get(
                    "tg",
                    "---",
                )
            )

            name = str(
                item.get(
                    "name",
                    "",
                )
            )

            talkers = item.get(
                "talkers",
                {},
            )

            calls = []

            if isinstance(
                talkers,
                dict,
            ):
                calls = list(
                    talkers.keys()
                )

            call_text = (
                ",".join(calls)
                if calls
                else "-"
            )

            d.text(
                (12, y),
                "TG " + tg,
                font=FONT_SMALL,
                fill="white",
            )

            d.text(
                (WIDTH - 12, y),
                call_text[:12],
                font=FONT_TINY,
                fill="white",
                anchor="ra",
            )

            d.text(
                (18, y + 18),
                name[:26],
                font=FONT_TINY,
                fill="white",
            )

            y += 36

    d.line(
        (12, 275, WIDTH - 12, 275),
        fill="white",
        width=1,
    )

    pass  # Footer button captions removed.

    footer_icons(img, left='back', right=None)
    write_fb(img)





def draw_last_qso():

    try:
        qso = controller.last_qso()

    except Exception as e:
        print(
            "LAST QSO PAGE ERROR:",
            e,
            flush=True,
        )
        qso = []

    img = Image.new(
        "RGB",
        (WIDTH, HEIGHT),
        theme.BG,
    )

    d = MenuDraw(img)

    d.text(
        (WIDTH // 2, 29),
        "Last QSO",
        font=FONT_MENU,
        fill="white",
        anchor="mm",
    )

    d.line(
        (12, 44, WIDTH - 12, 44),
        fill="white",
        width=1,
    )

    y = 58

    if not qso:

        d.text(
            (WIDTH // 2, 140),
            "No QSO data",
            font=FONT_MED,
            fill="white",
            anchor="mm",
        )

    else:

        for item in qso[:6]:

            call = str(
                item.get(
                    "call",
                    "---",
                )
            )

            tg = str(
                item.get(
                    "tg",
                    "---",
                )
            )

            start_time = str(
                item.get(
                    "start",
                    "--:--",
                )
            )

            duration = str(
                item.get(
                    "duration",
                    "0",
                )
            )

            d.text(
                (12, y),
                call[:14],
                font=FONT_SMALL,
                fill="white",
            )

            d.text(
                (WIDTH - 12, y),
                "TG" + tg,
                font=FONT_TINY,
                fill="white",
                anchor="ra",
            )

            d.text(
                (18, y + 18),
                start_time
                + "  "
                + duration
                + "s",
                font=FONT_TINY,
                fill="white",
            )

            y += 36

    d.line(
        (12, 275, WIDTH - 12, 275),
        fill="white",
        width=1,
    )

    pass  # Footer button captions removed.

    footer_icons(img, left='back', right=None)
    write_fb(img)






def load_station_list():
    try:
        stations = controller.stations()

        if isinstance(stations, list):
            return sorted(
                [str(x) for x in stations]
            )

    except Exception as e:
        print(
            "STATIONS ERROR:",
            e,
            flush=True,
        )

    return []



def draw_stations():
    global station_list
    global station_index

    station_list = load_station_list()

    if station_list:
        station_index %= len(station_list)
    else:
        station_index = 0

    img = Image.new(
        "RGB",
        (WIDTH, HEIGHT),
        theme.BG,
    )

    d = MenuDraw(img)

    d.text(
        (WIDTH // 2, 29),
        "Stations",
        font=FONT_MENU,
        fill="white",
        anchor="mm",
    )

    d.line(
        (12, 44, WIDTH - 12, 44),
        fill="white",
        width=1,
    )

    if not station_list:
        d.text(
            (WIDTH // 2, 140),
            "No stations",
            font=FONT_MED,
            fill="white",
            anchor="mm",
        )

    else:
        visible = 7

        start = max(
            0,
            min(
                station_index - 3,
                len(station_list) - visible,
            ),
        )

        end = min(
            len(station_list),
            start + visible,
        )

        y = 60

        for i in range(start, end):
            call = station_list[i]

            if i == station_index:
                d.rectangle(
                    (10, y - 4, WIDTH - 10, y + 26),
                    outline="white",
                    width=2,
                )

                text = "> " + call
            else:
                text = call

            d.text(
                (20, y + 9),
                text[:20],
                font=FONT_MENU_SMALL,
                fill="white",
                anchor="lm",
            )

            y += 30

    d.line(
        (12, 275, WIDTH - 12, 275),
        fill="white",
        width=1,
    )

    pass  # Footer button captions removed.

    pass  # Footer button captions removed.

    footer_icons(img, left='back', right='enter')
    write_fb(img)





def _node_value(node, *keys):
    for key in keys:
        value = node.get(key)

        if value not in (
            None,
            "",
            [],
            {},
        ):
            return value

    return None



def draw_station_detail():
    call = station_selected

    try:
        node = controller.station_details(call)
    except Exception as e:
        print(
            "STATION DETAIL ERROR:",
            e,
            flush=True,
        )
        node = {}

    img = Image.new(
        "RGB",
        (WIDTH, HEIGHT),
        theme.BG,
    )

    d = MenuDraw(img, panel=True)

    d.text(
        (WIDTH // 2, 29),
        str(call or "Station")[:18],
        font=FONT_MENU,
        fill="white",
        anchor="mm",
    )

    d.line(
        (12, 44, WIDTH - 12, 44),
        fill="white",
        width=1,
    )

    location = _node_value(
        node,
        "Location",
        "nodeLocation",
    )

    locator = _node_value(
        node,
        "Locator",
        "locator",
    )

    mode = _node_value(
        node,
        "Mode",
        "mode",
    )

    sysop = _node_value(
        node,
        "SysOp",
        "Sysop",
        "sysop",
    )

    default_tg = _node_value(
        node,
        "DefaultTG",
        "defaultTG",
    )

    monitored = _node_value(
        node,
        "monitoredTGs",
    )

    if isinstance(monitored, list):
        monitored = ",".join(
            str(x)
            for x in monitored[:6]
        )

    rows = [
        ("Location", location),
        ("Locator", locator),
        ("Mode", mode),
        ("SysOp", sysop),
        ("Default", default_tg),
        ("Mon TG", monitored),
    ]

    y = 60

    for label, value in rows:
        if value in (None, "", []):
            value = "-"

        d.text(
            (12, y),
            label + ":",
            font=FONT_TINY,
            fill="white",
        )

        d.text(
            (76, y),
            str(value)[:23],
            font=FONT_SMALL,
            fill="white",
        )

        y += 36

    d.line(
        (12, 275, WIDTH - 12, 275),
        fill="white",
        width=1,
    )

    pass  # Footer button captions removed.

    pass  # Footer button captions removed.

    footer_icons(img, left='back', right=None)
    write_fb(img)





def draw_node_info():
    try:
        node = controller.own_node_info()
    except Exception as e:
        print(
            "NODE INFO ERROR:",
            e,
            flush=True,
        )
        node = {}

    callsign = node.get(
        "callsign",
        controller.main_status().get(
            "callsign",
            "SQLink",
        ),
    )

    img = Image.new(
        "RGB",
        (WIDTH, HEIGHT),
        theme.BG,
    )

    d = MenuDraw(img, panel=True)

    d.text(
        (WIDTH // 2, 29),
        "Node Info",
        font=FONT_MENU,
        fill="white",
        anchor="mm",
    )

    d.line(
        (12, 44, WIDTH - 12, 44),
        fill="white",
        width=1,
    )

    rows = [
        (
            "Call",
            callsign,
        ),
        (
            "Location",
            _node_value(
                node,
                "Location",
                "nodeLocation",
            ),
        ),
        (
            "Locator",
            _node_value(
                node,
                "Locator",
                "locator",
            ),
        ),
        (
            "Mode",
            _node_value(
                node,
                "Mode",
                "mode",
            ),
        ),
        (
            "SysOp",
            _node_value(
                node,
                "SysOp",
                "Sysop",
                "sysop",
            ),
        ),
        (
            "TG",
            _node_value(
                node,
                "tg",
            ),
        ),
    ]

    y = 64

    for label, value in rows:
        if value in (None, "", []):
            value = "-"

        d.text(
            (12, y),
            label + ":",
            font=FONT_TINY,
            fill="white",
        )

        d.text(
            (76, y),
            str(value)[:23],
            font=FONT_SMALL,
            fill="white",
        )

        y += 36

    d.line(
        (12, 275, WIDTH - 12, 275),
        fill="white",
        width=1,
    )

    pass  # Footer button captions removed.

    footer_icons(img, left='back', right=None)
    write_fb(img)





def draw_sqlink_menu():
    img = Image.new("RGB", (WIDTH, HEIGHT), theme.BG)
    d = MenuDraw(img)

    d.text(
        (WIDTH // 2, 29),
        "SQLink",
        font=FONT_MENU,
        fill="white",
        anchor="mm",
    )

    d.line(
        (12, 43, WIDTH - 12, 43),
        fill="white",
        width=1,
    )

    # Six rows must fit between header and footer.
    top = 59
    row_h = 37

    for i, item in enumerate(SQLINK_MENU):
        y = top + i * row_h

        if i == menu_index:
            d.rectangle(
                (10, y - 4, WIDTH - 10, y + 27),
                outline="white",
                width=2,
            )

            text = "> " + item
        else:
            text = item

        d.text(
            (20, y + 10),
            text,
            font=FONT_MENU_SMALL,
            fill="white",
            anchor="lm",
        )

    d.line(
        (12, 276, WIDTH - 12, 276),
        fill="white",
        width=1,
    )

    pass  # Footer button captions removed.

    pass  # Footer button captions removed.

    footer_icons(img, left='back', right='enter')
    write_fb(img)





def draw_tg_menu():
    refresh_tg_list_if_needed()

    img = Image.new("RGB", (WIDTH, HEIGHT), theme.BG)
    d = MenuDraw(img)

    d.text(
        (WIDTH // 2, 29),
        "Talk Groups",
        font=FONT_MENU,
        fill="white",
        anchor="mm",
    )

    d.line((12, 46, WIDTH - 12, 46), fill="white", width=1)

    visible = 6

    start = max(
        0,
        min(
            tg_index - 2,
            len(TG_LIST) - visible,
        ),
    )

    end = min(
        len(TG_LIST),
        start + visible,
    )

    y = 58

    for i in range(start, end):
        tg, name = TG_LIST[i]

        if i == tg_index:
            d.rectangle(
                (8, y - 5, WIDTH - 8, y + 31),
                outline="white",
                width=2,
            )
            prefix = ">"
        else:
            prefix = " "

        d.text(
            (16, y + 7),
            prefix + " " + tg,
            font=FONT_MENU_SMALL,
            fill="white",
            anchor="lm",
        )

        d.text(
            (WIDTH - 12, y + 7),
            name[:14],
            font=FONT_TINY,
            fill="white",
            anchor="rm",
        )

        y += 35

    d.line((12, 273, WIDTH - 12, 273), fill="white", width=1)

    pass  # Footer button captions removed.

    pass  # Footer button captions removed.

    footer_icons(img, left='back', right='enter')
    write_fb(img)




def draw_submenu(title):
    img = Image.new("RGB", (WIDTH, HEIGHT), theme.BG)
    d = MenuDraw(img, panel=True)

    d.text(
        (WIDTH // 2, 29),
        title,
        font=FONT_MENU,
        fill="white",
        anchor="mm",
    )

    d.line((12, 50, WIDTH - 12, 50), fill="white", width=1)

    d.text(
        (WIDTH // 2, 135),
        "Menu in build",
        font=FONT_MED,
        fill="white",
        anchor="mm",
    )

    d.text(
        (WIDTH // 2, 170),
        "BACK = return",
        font=FONT_SMALL,
        fill="white",
        anchor="mm",
    )

    footer_icons(img, left='back', right=None)
    write_fb(img)





def redraw():
    if not menu_mode:
        draw_main()
    elif submenu == "User":
        write_fb(user_menu.render())
    elif submenu == "Audio":
        write_fb(audio_menu.render())
    elif submenu == "Bluetooth":
        write_fb(bluetooth_menu.render())
    elif submenu == "Restart":
        write_fb(restart_menu.render())
    elif submenu == "Display":
        write_fb(display_menu.render())
    elif submenu == "WiFi":
        write_fb(wifi_menu.render())
    elif submenu == "SQLink":
        draw_sqlink_menu()
    elif submenu == "Talk Groups":
        draw_tg_menu()
    elif submenu == "Network":
        draw_network()
    elif submenu == "Active TG":
        draw_active_tg()
    elif submenu == "Last QSO":
        draw_last_qso()
    elif submenu == "Stations":
        draw_stations()
    elif submenu == "Station Detail":
        draw_station_detail()
    elif submenu == "Node Info":
        draw_node_info()
    elif submenu:
        draw_submenu(submenu)
    else:
        draw_menu()



def handle_button(name):
    global menu_mode
    global submenu
    global menu_index
    global tg_index
    global station_index
    global station_selected
    global station_list

    if not menu_mode:
        if name in ("BACK", "UP"):
            return
        if name == "ENTER":
            menu_mode = True
            submenu = None
            menu_index = 0
            redraw()
        elif name == "DOWN":
            menu_mode = True
            submenu = "Talk Groups"
            tg_index = 0
            redraw()
        return

    if submenu == "User":
        if user_menu.button(name):
            submenu = None
            menu_index = MAIN_MENU.index("User")
        redraw()
        return

    if submenu == "Audio":
        if audio_menu.button(name):
            submenu = None
            menu_index = MAIN_MENU.index("Audio")
        redraw()
        return

    if submenu == "Bluetooth":
        if bluetooth_menu.button(name):
            submenu = None
            menu_index = MAIN_MENU.index("Bluetooth")
        redraw()
        return

    if submenu == "Restart":
        if restart_menu.button(name):
            submenu = None
            menu_index = MAIN_MENU.index("Restart")
        redraw()
        return

    if submenu == "Display":
        if display_menu.button(name):
            submenu = None
            menu_index = MAIN_MENU.index("Display")
        redraw()
        return

    if submenu == "WiFi":
        if wifi_menu.button(name):
            submenu = None
            menu_index = MAIN_MENU.index("WiFi")
        redraw()
        return

    if submenu == "Stations":

        if name == "BACK":
            submenu = "SQLink"
            menu_index = 3
            redraw()
            return

        if not station_list:
            redraw()
            return

        if name == "UP":
            station_index = (
                station_index - 1
            ) % len(station_list)

            redraw()
            return

        if name == "DOWN":
            station_index = (
                station_index + 1
            ) % len(station_list)

            redraw()
            return

        if name == "ENTER":
            station_selected = (
                station_list[
                    station_index
                ]
            )

            submenu = "Station Detail"

            redraw()
            return

    if submenu == "Station Detail":

        if name == "BACK":
            submenu = "Stations"
            redraw()
            return

        # ENTER intentionally reserved for future QRZ action.
        return

    if submenu == "Talk Groups":

        if name == "BACK":
            submenu = "SQLink"
            menu_index = 5
            redraw()
            return

        if name == "UP":
            tg_index = (tg_index - 1) % len(TG_LIST)
            redraw()
            return

        if name == "DOWN":
            tg_index = (tg_index + 1) % len(TG_LIST)
            redraw()
            return

        if name == "ENTER":
            selected_tg = TG_LIST[tg_index][0]

            if select_tg(selected_tg):
                submenu = None
                menu_mode = False
                set_message("TG " + selected_tg, 2.0)

            redraw()
            return

    if submenu == "SQLink":

        if name == "BACK":
            submenu = None
            menu_index = 0
            redraw()
            return

        if name == "UP":
            menu_index = (menu_index - 1) % len(SQLINK_MENU)
            redraw()
            return

        if name == "DOWN":
            menu_index = (menu_index + 1) % len(SQLINK_MENU)
            redraw()
            return

        if name == "ENTER":
            selected = SQLINK_MENU[menu_index]

            if selected == "Talk Groups":
                submenu = "Talk Groups"
                tg_index = 0

            else:
                submenu = selected

            redraw()
            return

    if submenu:

        if name == "BACK":

            sqlink_pages = {
                "Network": 0,
                "Active TG": 1,
                "Last QSO": 2,
                "Stations": 3,
                "Node Info": 4,
            }

            if submenu in sqlink_pages:
                menu_index = sqlink_pages[submenu]
                submenu = "SQLink"
            else:
                submenu = None

            redraw()

        return

    if name == "BACK":
        menu_mode = False
        submenu = None
        redraw()
        return

    if name == "UP":
        menu_index = (menu_index - 1) % len(MAIN_MENU)
        redraw()
        return

    if name == "DOWN":
        menu_index = (menu_index + 1) % len(MAIN_MENU)
        redraw()
        return

    if name == "ENTER":
        selected = MAIN_MENU[menu_index]

        if selected == "SQLink":
            submenu = "SQLink"
            menu_index = 0
        else:
            submenu = selected
            if selected == "User":
                user_menu.enter()
            if selected == "Audio":
                audio_menu.enter()
            if selected == "Bluetooth":
                bluetooth_menu.enter()
            if selected == "Restart":
                restart_menu.enter()
            if selected == "Display":
                display_menu.enter()
            if selected == "WiFi":
                wifi_menu.enter()

        redraw()



MENU_IDLE_SECONDS = 30.0
last_menu_activity = time.monotonic()


def return_home_if_idle(now):
    global menu_mode, submenu, menu_index, message, message_until
    timeout = display_settings.values['idle_timeout']
    if not menu_mode or timeout == 0 or now - last_menu_activity < timeout:
        return False
    menu_mode = False
    submenu = None
    menu_index = 0
    message = ""
    message_until = 0.0
    user_menu.cancel()
    bluetooth_menu.cancel()
    display_menu.cancel()
    wifi_menu.password = ""
    redraw()
    return True


TG_LIST = load_tg_list()

h = lgpio.gpiochip_open(0)

for pin in BUTTONS:
    lgpio.gpio_claim_input(
        h,
        pin,
        lgpio.SET_PULL_UP,
    )

button_last = {}
button_time = {}

for pin in BUTTONS:
    button_last[pin] = lgpio.gpio_read(h, pin)
    button_time[pin] = 0.0

last_redraw = 0.0
last_profile_key = profile_state.key()
profile_checked = 0.0

try:
    redraw()

    while True:
        now = time.monotonic()
        if now-profile_checked >= 1:
            profile_checked=now
            key=profile_state.key()
            if key!=last_profile_key:
                last_profile_key=key;TG_LIST=load_tg_list();tg_index=0;_main_state_time=0
                redraw()

        if user_menu.poll() and submenu == "User":
            redraw()

        if audio_menu.poll() and submenu == "Audio":
            redraw()

        if bluetooth_menu.poll() and submenu == "Bluetooth":
            redraw()

        if restart_menu.poll() and submenu == "Restart":
            redraw()

        if wifi_menu.poll() and submenu == "WiFi":
            redraw()

        for pin, name in BUTTONS.items():
            state = lgpio.gpio_read(h, pin)

            if state == 0:
                last_menu_activity = now

            if state == button_last[pin]:
                continue

            if now - button_time[pin] < 0.035:
                continue

            button_time[pin] = now
            button_last[pin] = state
            last_menu_activity = now

            if state == 0:
                print("BUTTON:", name, flush=True)
                handle_button(name)

        if return_home_if_idle(time.monotonic()):
            last_redraw = time.monotonic()

        if not menu_mode and (now - last_redraw) >= (0.1 if radio_status.mode == "RX" else 0.25 if radio_status.mode == "TX" else 1.0):
            draw_main()
            last_redraw = now

        time.sleep(0.01)

finally:
    lgpio.gpiochip_close(h)
