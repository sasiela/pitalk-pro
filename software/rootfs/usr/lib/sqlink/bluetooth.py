import subprocess


def _ctl(*args):
    return subprocess.run(
        ["bluetoothctl", *args],
        capture_output=True,
        text=True,
        timeout=5,
    )


def controller_info():
    result = _ctl("show")

    info = {
        "available": result.returncode == 0,
        "powered": False,
        "pairable": False,
        "discoverable": False,
    }

    for raw in result.stdout.splitlines():
        line = raw.strip()

        if line.startswith("Powered:"):
            info["powered"] = (
                line.split(":", 1)[1].strip() == "yes"
            )

        elif line.startswith("Pairable:"):
            info["pairable"] = (
                line.split(":", 1)[1].strip() == "yes"
            )

        elif line.startswith("Discoverable:"):
            info["discoverable"] = (
                line.split(":", 1)[1].strip() == "yes"
            )

    return info


def power(on=True):
    result = _ctl(
        "power",
        "on" if on else "off",
    )

    return result.returncode == 0


def devices():
    result = _ctl("devices")

    output = []

    for line in result.stdout.splitlines():
        if not line.startswith("Device "):
            continue

        parts = line.split(" ", 2)

        if len(parts) == 3:
            output.append({
                "mac": parts[1],
                "name": parts[2],
            })

    return output


def connect(mac):
    return _ctl("connect", mac).returncode == 0


def disconnect(mac):
    return _ctl("disconnect", mac).returncode == 0
