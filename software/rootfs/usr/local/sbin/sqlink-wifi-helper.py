#!/usr/bin/python3
"""Local SQLink Wi-Fi operations. Never log request bodies or NM stderr."""
import configparser
import grp
import io
import json
import os
import pathlib
import socketserver
import subprocess
import uuid

SOCKET = '/run/sqlink-wifi/control.sock'
ENV = dict(os.environ, LC_ALL='C', LANG='C')


def nm(*args, timeout=12):
    r = subprocess.run(['/usr/bin/nmcli', '--colors', 'no', *args],
                       capture_output=True, text=True, env=ENV, timeout=timeout)
    if r.returncode:
        raise RuntimeError('Operacja Wi-Fi nie powiodla sie.')
    return r.stdout.rstrip('\n')


def fields(line):
    result, part, escaped = [], '', False
    for c in line:
        if escaped:
            part += c
            escaped = False
        elif c == '\\':
            escaped = True
        elif c == ':':
            result.append(part)
            part = ''
        else:
            part += c
    if escaped:
        part += '\\'
    return result + [part]


def values(*args):
    return [fields(x)[0] for x in nm(*args).splitlines()]


def saved():
    result = []
    for line in nm('-t', '-f', 'UUID,TYPE', 'connection', 'show').splitlines():
        ident, kind = fields(line)
        if kind != '802-11-wireless':
            continue
        data = values('-g', 'connection.id,802-11-wireless.ssid,connection.interface-name,connection.autoconnect-priority,connection.autoconnect',
                      'connection', 'show', 'uuid', ident)
        if len(data) >= 2 and (len(data) < 3 or data[2] in ('', 'wlan0')):
            result.append(dict(uuid=ident, name=data[0], ssid=data[1],
                               priority=int(data[3]), autoconnect=data[4] == 'yes'))
    eligible = [p for p in result if p['autoconnect']]
    highest = max((p['priority'] for p in eligible), default=0)
    leaders = [p for p in eligible if p['priority'] == highest]
    for p in result:
        p['default'] = highest > 0 and len(leaders) == 1 and p['uuid'] == leaders[0]['uuid']
    return result


def status():
    data = values('-g', 'GENERAL.STATE,GENERAL.CON-UUID,IP4.ADDRESS',
                  'device', 'show', 'wlan0')
    profiles = saved()
    ident = data[1] if len(data) > 1 else ''
    current = next((p['ssid'] for p in profiles if p['uuid'] == ident), '')
    return dict(connected=bool(data and data[0].split(' ')[0] == '100'),
                uuid=ident, ssid=current, ip=data[2] if len(data) > 2 else '',
                radio=nm('radio', 'wifi') == 'enabled', saved=profiles)


def scan(rescan=False):
    found = {}
    for line in nm('-t', '-f', 'IN-USE,SSID,SIGNAL,SECURITY', 'device', 'wifi',
                   'list', 'ifname', 'wlan0', '--rescan', 'yes' if rescan else 'no',
                   timeout=25).splitlines():
        data = fields(line)
        if len(data) != 4 or not data[1]:
            continue
        active, ssid, signal, security = data
        row = dict(ssid=ssid, signal=int(signal), security=security,
                   active=active == '*', enterprise=('802.1X' in security or 'EAP' in security),
                   supported=(security in ('', '--') or
                              ('WPA' in security and '802.1X' not in security and 'EAP' not in security)))
        if ssid not in found or row['signal'] > found[ssid]['signal']:
            found[ssid] = row
    return sorted(found.values(), key=lambda r: (-r['active'], -r['signal'], r['ssid']))


def activate(ident):
    nm('-w', '30', 'connection', 'up', 'uuid', ident, 'ifname', 'wlan0', timeout=35)


def connect(request):
    before = status()
    previous = before['uuid'] if before['connected'] else ''
    new_id, path = None, None
    try:
        ident = request.get('uuid')
        if ident:
            if ident not in {p['uuid'] for p in before['saved']}:
                raise ValueError('Nie znaleziono profilu Wi-Fi.')
        else:
            ssid = request.get('ssid')
            if not isinstance(ssid, str) or not 1 <= len(ssid.encode()) <= 32 or '\x00' in ssid:
                raise ValueError('Nieprawidlowa nazwa sieci.')
            access = next((r for r in scan() if r['ssid'] == ssid), None)
            if not access or not access['supported']:
                raise ValueError('Siec niedostepna lub nieobslugiwane zabezpieczenia.')
            password = request.get('password', '')
            protected = access['security'] not in ('', '--')
            if protected and (not isinstance(password, str) or
                              not (8 <= len(password) <= 63 or
                                   len(password) == 64 and all(c in '0123456789abcdefABCDEF' for c in password)) or
                              any(ord(c) < 32 or ord(c) > 126 for c in password)):
                raise ValueError('Haslo: 8-63 znaki lub 64 cyfry hex.')
            ident = new_id = str(uuid.uuid4())
            raw = nm('--offline', 'connection', 'add', 'type', 'wifi', 'ifname', 'wlan0',
                     'con-name', ssid, 'ssid', ssid, 'connection.uuid', ident,
                     'connection.autoconnect', 'no', 'ipv4.method', 'auto', 'ipv6.method', 'auto')
            conf = configparser.ConfigParser(interpolation=None)
            conf.read_string(raw)
            if protected:
                conf['wifi-security'] = {'key-mgmt': 'sae' if access['security'] == 'WPA3' else 'wpa-psk',
                                         'psk': password, 'psk-flags': '0'}
            # GLib keyfile escaping preserves leading/trailing spaces and backslashes.
            if protected:
                conf['wifi-security']['psk'] = password.replace('\\', '\\\\').replace(' ', '\\s')
            buffer = io.StringIO()
            conf.write(buffer, space_around_delimiters=False)
            path = pathlib.Path('/etc/NetworkManager/system-connections') / ('sqlink-' + ident + '.nmconnection')
            fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            with os.fdopen(fd, 'w') as out:
                out.write(buffer.getvalue())
                out.flush()
                os.fsync(out.fileno())
            nm('connection', 'load', str(path))
        nm('radio', 'wifi', 'on')
        activate(ident)
        nm('connection', 'modify', 'uuid', ident, 'connection.autoconnect', 'yes')
        return dict(ok=True, message='Polaczono. Profil zapisany.', status=status())
    except Exception:
        if new_id:
            try:
                nm('connection', 'delete', 'uuid', new_id)
            except Exception:
                pass
            if path:
                path.unlink(missing_ok=True)
        restored = False
        if previous:
            try:
                activate(previous)
                restored = True
            except Exception:
                pass
        return dict(ok=False, message=('Blad polaczenia. Poprzednia siec przywrocona.' if restored
                                      else 'Nie polaczono. Sprawdz haslo i zasieg.'))


def set_default(ident):
    profiles = saved()
    selected = next((p for p in profiles if p['uuid'] == ident), None)
    if selected is None:
        return dict(ok=False, message='Nie znaleziono profilu Wi-Fi.')
    changed = []
    try:
        # Highest supported NM priority. Preserve other priorities unless tied.
        for profile in profiles:
            if profile['uuid'] != ident and profile['priority'] >= 999:
                changed.append(profile)
                nm('connection', 'modify', 'uuid', profile['uuid'],
                   'connection.autoconnect-priority', '998')
        changed.append(selected)
        nm('connection', 'modify', 'uuid', ident,
           'connection.autoconnect', 'yes', 'connection.autoconnect-priority', '999')
        return dict(ok=True, message='Zapisano profil domyslny.', status=status())
    except Exception:
        restored = True
        for profile in reversed(changed):
            try:
                nm('connection', 'modify', 'uuid', profile['uuid'],
                   'connection.autoconnect', 'yes' if profile['autoconnect'] else 'no',
                   'connection.autoconnect-priority', str(profile['priority']))
            except Exception:
                restored = False
        return dict(ok=False, message=('Blad zapisu. Przywrocono priorytety.' if restored
                                      else 'Blad zapisu. Sprawdz priorytety sieci.'))


def dispatch(request):
    action = request.get('action')
    if action == 'web_auth':
        from sqlink_web_auth import authenticate
        return dict(ok=True, authenticated=authenticate(request.get('username'), request.get('password')))
    if action in ('profiles_snapshot','profiles_save','profiles_activate','profiles_default','profiles_delete'):
        import sqlink_profiles
        return sqlink_profiles.dispatch(request)
    if action == 'user_save':
        return dict(ok=False,message='Reload the panel and use Profiles to edit connection settings.')
    if action in ('user_snapshot',):
        import sqlink_user_config
        return sqlink_user_config.dispatch(request)
    if action == 'restart_device':
        if request.get('confirm') is not True:
            return dict(ok=False, message='Confirmation required.')
        try:
            if pathlib.Path('/sys/class/gpio/gpio536/value').read_text().strip() != '1':
                return dict(ok=False, message='Release PTT before restart.')
            result = subprocess.run(['/usr/bin/systemd-run', '--quiet',
                '--unit=sqlink-user-reboot', '--on-active=2s',
                '/usr/bin/systemctl', 'reboot'], capture_output=True, timeout=5)
            if result.returncode:
                return dict(ok=False, message='Could not schedule restart.')
            return dict(ok=True, message='Restarting device...')
        except Exception:
            return dict(ok=False, message='Restart request failed.')

    if action == 'snapshot':
        return dict(ok=True, status=status(), networks=scan())
    if action == 'scan':
        nm('radio', 'wifi', 'on')
        networks = scan(True)
        return dict(ok=True, status=status(), networks=networks)
    if action == 'set_default':
        return set_default(request.get('uuid'))
    if action == 'connect':
        return connect(request)
    raise ValueError('Nieznana operacja.')


class Handler(socketserver.StreamRequestHandler):
    def handle(self):
        self.request.settimeout(5)
        try:
            line = self.rfile.readline(4097)
            if len(line) > 4096:
                raise ValueError()
            request = json.loads(line)
            if not isinstance(request, dict):
                raise ValueError()
            response = dispatch(request)
        except Exception:
            response = dict(ok=False, message='Blad uslugi Wi-Fi. Sprobuj ponownie.')
        try:
            self.wfile.write((json.dumps(response) + '\n').encode())
        except (BrokenPipeError, ConnectionError):
            pass


if __name__ == '__main__':
    import sys
    if '--snapshot' in sys.argv:
        print(json.dumps(dispatch(dict(action='snapshot'))))
    else:
        pathlib.Path(SOCKET).unlink(missing_ok=True)
        with socketserver.UnixStreamServer(SOCKET, Handler) as server:
            os.chown(SOCKET, 0, grp.getgrnam('sqlink').gr_gid)
            os.chmod(SOCKET, 0o660)
            server.serve_forever()
