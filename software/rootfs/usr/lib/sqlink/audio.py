import os
import subprocess


def runtime_dir():
    return "/run/user/" + str(os.getuid())


def _pactl(*args):
    env = os.environ.copy()

    if "XDG_RUNTIME_DIR" not in env:
        env["XDG_RUNTIME_DIR"] = runtime_dir()

    return subprocess.run(
        ["pactl", *args],
        capture_output=True,
        text=True,
        env=env,
        timeout=4,
    )


def get_default_sink():
    result = _pactl("get-default-sink")

    if result.returncode != 0:
        return None

    return result.stdout.strip()


def get_default_source():
    result = _pactl("get-default-source")

    if result.returncode != 0:
        return None

    return result.stdout.strip()


def set_source_mute(source, muted):
    result = _pactl(
        "set-source-mute",
        source,
        "1" if muted else "0",
    )

    return result.returncode == 0


def get_status():
    return {
        "sink": get_default_sink(),
        "source": get_default_source(),
    }
