import json
import time
import urllib.request
import urllib.error


STATUS_URL = "https://sqlink.pl/api.php?since=0"
TG_NAMES_URL = "https://sqlink.pl/tg_names.json"

USER_AGENT = "SQLink-Pi/0.1"

_tg_cache = None
_tg_cache_time = 0.0

_status_cache = None
_status_cache_time = 0.0

TG_CACHE_TTL = 600
STATUS_CACHE_TTL = 5


def _get_json(url, timeout=5):
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
        },
    )

    with urllib.request.urlopen(
        req,
        timeout=timeout,
    ) as response:

        raw = response.read().decode(
            "utf-8",
            errors="ignore",
        )

    return json.loads(raw)


def get_status(timeout=5, force=False):
    global _status_cache
    global _status_cache_time

    now = time.monotonic()

    if (
        not force
        and _status_cache is not None
        and (now - _status_cache_time) < STATUS_CACHE_TTL
    ):
        return _status_cache

    url = (
        STATUS_URL
        + "&_="
        + str(time.time_ns())
    )

    try:
        data = _get_json(
            url,
            timeout,
        )

        if isinstance(data, dict):
            _status_cache = data
            _status_cache_time = now
            return data

    except urllib.error.HTTPError as e:

        # Some SQLink API responses may return 304.
        # 304 is not an offline indication.
        if e.code == 304:
            if _status_cache is not None:
                return _status_cache

            return {}

        raise

    if _status_cache is not None:
        return _status_cache

    return {}


def get_talkgroups(timeout=5, force=False):
    global _tg_cache
    global _tg_cache_time

    now = time.monotonic()

    if (
        not force
        and _tg_cache is not None
        and (now - _tg_cache_time) < TG_CACHE_TTL
    ):
        return _tg_cache

    url = (
        TG_NAMES_URL
        + "?_="
        + str(time.time_ns())
    )

    data = _get_json(
        url,
        timeout,
    )

    if not isinstance(data, list):
        raise ValueError(
            "tg_names.json is not a list"
        )

    result = []

    for item in data:

        if not isinstance(item, dict):
            continue

        tg = str(
            item.get("id", "")
        ).strip()

        name = str(
            item.get("name", "")
        ).strip()

        if not tg.isdigit():
            continue

        if int(tg) <= 0:
            continue

        if not name:
            name = "TG " + tg

        result.append({
            "id": int(tg),
            "name": name,
        })

    unique = {
        item["id"]: item
        for item in result
    }

    _tg_cache = [
        unique[tg]
        for tg in sorted(unique)
    ]

    _tg_cache_time = now

    return _tg_cache


def get_tg_name(tg):

    try:
        tg_num = int(tg)

    except (TypeError, ValueError):
        return None

    try:

        for item in get_talkgroups():

            if item["id"] == tg_num:
                return item["name"]

    except Exception:
        return None

    return None
