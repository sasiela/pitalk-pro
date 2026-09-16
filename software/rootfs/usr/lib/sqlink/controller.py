from . import api
from . import audio
from . import bluetooth
from . import gpio
from . import network
from . import reflector


class SQLinkController:

    def main_status(self):
        """
        Fast status for the PiTFT main screen.

        Does NOT query:
        - NetworkManager
        - PipeWire
        - bluetoothctl
        - server status API

        Only local SvxLink state is read.
        """
        log = reflector.read_recent_log()

        active_tg = reflector.get_active_tg(log)

        active_tg_name = (
            api.get_tg_name(active_tg)
            if active_tg
            else None
        )

        return {
            "callsign": reflector.get_callsign(),

            "reflector": {
                "connected": reflector.is_connected(log),
                "active_tg": active_tg,
                "active_tg_name": active_tg_name,
                "default_tg": reflector.get_default_tg(),
            },

            "ptt": (
                gpio.is_ptt_active()
                if gpio.available()
                else False
            ),
        }


    def status(self):
        log = reflector.read_recent_log()

        active_tg = reflector.get_active_tg(log)
        active_tg_name = (
            api.get_tg_name(active_tg)
            if active_tg
            else None
        )

        return {
            "callsign": reflector.get_callsign(),

            "reflector": {
                "connected": reflector.is_connected(log),
                "active_tg": active_tg,
                "active_tg_name": active_tg_name,
                "default_tg": reflector.get_default_tg(),
            },

            "network": network.get_status(),
            "audio": audio.get_status(),
            "bluetooth": bluetooth.controller_info(),

            "ptt": (
                gpio.is_ptt_active()
                if gpio.available()
                else False
            ),
        }

    def select_tg(self, tg):
        return reflector.select_tg(tg)

    def ptt_on(self):
        gpio.ptt_on()

    def ptt_off(self):
        gpio.ptt_off()

    def talkgroups(self):
        return api.get_talkgroups()

    def server_status(self):
        return api.get_status()

    def network_page(self):
        # ONLINE/OFFLINE must always come from the
        # actual SvxLink reflector connection.
        log = reflector.read_recent_log()

        result = {
            "connected": reflector.is_connected(log),
            "server": "sqlink.pl",
            "stations_count": None,
            "uptime": None,
        }

        # Server API provides supplemental information only.
        # API failure must never turn an authenticated
        # reflector connection into OFFLINE on the UI.
        try:
            data = self.server_status()

            if isinstance(data, dict):
                result["stations_count"] = data.get(
                    "stations_count"
                )
                result["uptime"] = data.get(
                    "uptime"
                )

        except Exception:
            pass

        return result

    def active_talkgroups(self):
        data = self.server_status()

        active = data.get("active_tg", [])

        if not isinstance(active, list):
            return []

        return active

    def last_qso(self):
        data = self.server_status()

        qso = data.get("qso", [])

        if not isinstance(qso, list):
            return []

        return qso

    def stations(self):
        data = self.server_status()

        stations = data.get("stations", [])

        if not isinstance(stations, list):
            return []

        return stations

    def station_details(self, callsign):
        data = self.server_status()

        nodes = data.get("statusNodes", {})

        if not isinstance(nodes, dict):
            return {}

        node = nodes.get(callsign)

        if not isinstance(node, dict):
            return {}

        result = dict(node)
        result["callsign"] = callsign

        return result

    def own_node_info(self):
        callsign = reflector.get_callsign()
        return self.station_details(callsign)

    def alerts(self):
        data = self.server_status()

        alerts = data.get("alerts", [])

        if not isinstance(alerts, list):
            return []

        return alerts
