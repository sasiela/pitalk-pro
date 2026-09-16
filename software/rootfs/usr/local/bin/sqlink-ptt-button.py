#!/usr/bin/python3
"""Hold-to-talk GPIO26 input; GPIO24 output remains owned by SQLink."""
import argparse
import signal
import socket
import sys
import os
import time


class Button:
    def __init__(self):
        self.raw = None
        self.since = 0.0
        self.stable = None
        self.armed = False
        self.active = False

    def update(self, level, now):
        if level not in (0, 1):
            raise RuntimeError("Invalid GPIO input")
        if level != self.raw:
            self.raw, self.since = level, now
        if now - self.since < 0.030 or level == self.stable:
            return None
        self.stable = level
        if level == 1:
            self.armed = True
        active = self.armed and level == 0
        if active == self.active:
            return None
        self.active = active
        return active


def notify(message):
    address = os.environ.get("NOTIFY_SOCKET")
    if not address:
        return
    if address.startswith("@"):
        address = "\0" + address[1:]
    with socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM) as sock:
        sock.sendto(message.encode(), address)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--release", action="store_true")
    args = parser.parse_args()
    sys.path.insert(0, "/usr/lib")
    from sqlink import gpio
    if args.release:
        gpio.ptt_off()
        return
    import lgpio
    running = True

    def stop(signum, frame):
        nonlocal running
        running = False

    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    handle = None
    try:
        if not args.dry_run:
            gpio.ptt_off()
        handle = lgpio.gpiochip_open(0)
        lgpio.gpio_claim_input(handle, 26, lgpio.SET_PULL_UP)
        button = Button()
        print("GPIO26 ready; debounce=30ms; release before first press; dry_run="
              + str(args.dry_run), flush=True)
        notify("READY=1")
        last_watchdog = 0.0
        while running:
            now = time.monotonic()
            change = button.update(lgpio.gpio_read(handle, 26), now)
            if change is not None:
                if not args.dry_run:
                    (gpio.ptt_on if change else gpio.ptt_off)()
                print("PTT ON" if change else "PTT OFF", flush=True)
            if now - last_watchdog >= 0.5:
                notify("WATCHDOG=1")
                last_watchdog = now
            time.sleep(0.005)
    finally:
        try:
            if not args.dry_run:
                gpio.ptt_off()
            print("PTT monitor stopped", flush=True)
        finally:
            if handle is not None:
                lgpio.gpiochip_close(handle)


if __name__ == "__main__":
    main()
