import subprocess


def _run(args, timeout=3):
    return subprocess.run(
        args,
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def get_wifi():
    try:
        result = _run([
            "nmcli",
            "-t",
            "-f",
            "GENERAL.STATE,GENERAL.CONNECTION",
            "device",
            "show",
            "wlan0",
        ])

        connected = False

        for line in result.stdout.splitlines():
            if line.startswith("GENERAL.STATE:"):
                connected = line.split(":", 1)[1].strip().split(" ")[0] == "100"

        ssid = None

        if connected:
            wifi = _run([
                "nmcli",
                "-t",
                "-f",
                "ACTIVE,SSID",
                "device",
                "wifi",
                "list",
                "ifname",
                "wlan0",
            ])

            for line in wifi.stdout.splitlines():
                if line.startswith("yes:"):
                    ssid = line.split(":", 1)[1]
                    break

        return {
            "connected": connected,
            "ssid": ssid,
        }

    except Exception:
        return {
            "connected": False,
            "ssid": None,
        }


def get_ip():
    try:
        result = _run([
            "ip",
            "-4",
            "-o",
            "addr",
            "show",
            "dev",
            "wlan0",
        ])

        for line in result.stdout.splitlines():
            parts = line.split()

            if "inet" in parts:
                idx = parts.index("inet")
                return parts[idx + 1].split("/")[0]

    except Exception:
        pass

    return None


def get_status():
    return {
        "wifi": get_wifi(),
        "ip": get_ip(),
    }
