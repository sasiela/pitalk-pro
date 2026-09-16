import os
import re


CONFIG = "/etc/svxlink/svxlink.conf"
LOG = "/var/log/svxlink"
DTMF = "/dev/shm/sqlink_dtmf"


def get_config_value(section, key, default=None):
    current = None

    try:
        with open(CONFIG, "r", errors="ignore") as f:
            for raw in f:
                line = raw.strip()

                if line.startswith("[") and line.endswith("]"):
                    current = line[1:-1]
                    continue

                if (
                    current == section
                    and line.startswith(key + "=")
                ):
                    return (
                        line.split("=", 1)[1]
                        .strip()
                        .strip('"')
                    )

    except OSError:
        pass

    return default


def get_callsign():
    return get_config_value(
        "SimplexLogic",
        "CALLSIGN",
        "SQLink",
    )


def get_default_tg():
    return get_config_value(
        "ReflectorLogic",
        "DEFAULT_TG",
        None,
    )


def read_recent_log(size=65536):
    try:
        with open(LOG, "rb") as f:
            f.seek(0, os.SEEK_END)
            total = f.tell()
            f.seek(max(0, total - size))

            return f.read().decode(
                "utf-8",
                errors="ignore",
            )
    except OSError:
        return ""


def get_active_tg(log=None):
    if log is None:
        log = read_recent_log()

    patterns = [
        r"Selecting TG #(\d+)",
        r"Talker start on TG #(\d+):",
    ]

    matches = []

    for pattern in patterns:
        for match in re.finditer(pattern, log):
            matches.append(
                (match.start(), match.group(1))
            )

    if not matches:
        return None

    matches.sort(key=lambda item: item[0])

    return matches[-1][1]


_connection_cache = (None, False)


def connection_event(log):
    events = [(log.rfind("ReflectorLogic: Authentication OK"), True)]
    for marker in ("ReflectorLogic: Disconnected from", "ReflectorLogic: Heartbeat timeout", "Starting logic: ReflectorLogic"):
        events.append((log.rfind(marker), False))
    position, connected = max(events, key=lambda item: item[0])
    return connected if position >= 0 else None


def is_connected(log=None):
    # Connection events can be much older than the recent activity window.
    global _connection_cache
    try:
        with open('/run/svxlink.pid') as f:
            pid = int(f.read().strip())
        with open('/proc/%d/comm' % pid) as f:
            if f.read().strip() != 'svxlink':return False
        st = os.stat(LOG)
        key = (pid, st.st_ino, st.st_size, st.st_mtime_ns)
        if key == _connection_cache[0]:return _connection_cache[1]
        result = None
        # Rotation moves the authentication event to older files.
        for path in [LOG] + [LOG + '.' + str(i) for i in range(1, 8)]:
            if result is not None:break
            try:
                with open(path, 'rb') as f:
                    f.seek(0, os.SEEK_END)
                    end = f.tell()
                    suffix = b''
                    while end and result is None:
                        start = max(0, end - 65536)
                        f.seek(start)
                        chunk = f.read(end-start)
                        result = connection_event((chunk+suffix).decode('utf-8', errors='ignore'))
                        suffix = chunk[:256]
                        end = start
            except FileNotFoundError:
                continue
        connected = result is True
        _connection_cache = (key, connected)
        return connected
    except (OSError, ValueError):
        return False


def select_tg(tg, timeout=5.0):
    import time

    tg = str(tg).strip()

    if not tg.isdigit():
        raise ValueError("Invalid TG")

    command = "91" + tg + "#"

    deadline = time.monotonic() + timeout
    last_error = None

    while time.monotonic() < deadline:

        try:
            if not os.path.lexists(DTMF):
                last_error = FileNotFoundError(
                    "DTMF symlink missing: " + DTMF
                )
                time.sleep(0.1)
                continue

            target = os.path.realpath(DTMF)

            if not os.path.exists(target):
                last_error = FileNotFoundError(
                    "DTMF PTY target missing: " + target
                )
                time.sleep(0.1)
                continue

            fd = os.open(
                DTMF,
                os.O_WRONLY | os.O_NOCTTY
            )

            try:
                os.write(
                    fd,
                    command.encode("ascii")
                )
            finally:
                os.close(fd)

            return command

        except OSError as e:
            last_error = e
            time.sleep(0.1)

    if last_error:
        raise RuntimeError(
            "DTMF unavailable after "
            + str(timeout)
            + "s: "
            + str(last_error)
        )

    raise RuntimeError("DTMF unavailable")

