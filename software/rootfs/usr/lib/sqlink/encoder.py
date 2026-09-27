"""EC11 on BCM 5/6/13. Callbacks collect edges; UI consumes actions."""
from collections import deque
from threading import Lock

class Decoder:
    # Positive sequence: 11 -> 01 -> 00 -> 10 -> 11.
    DELTA = {(3,1):1,(1,0):1,(0,2):1,(2,3):1,
             (1,3):-1,(0,1):-1,(2,0):-1,(3,2):-1}

    def __init__(self, state=3):
        self.state = state
        self.steps = 0
        self.anchor = state

    def update(self, state):
        if state == self.state:
            return None
        delta = self.DELTA.get((self.state, state))
        self.state = state
        if delta is None:
            self.steps = 0
            return None
        self.steps += delta
        if state == self.anchor:
            steps, self.steps = self.steps, 0
            if steps >= 4:
                return 'DOWN'
            if steps <= -4:
                return 'UP'
        return None

class Encoder:
    def __init__(self, gpio, handle):
        self.gpio, self.handle = gpio, handle
        self.lock = Lock()
        self.events = deque(maxlen=128)
        self.callbacks = []
        for pin in (5,6):
            gpio.gpio_claim_alert(handle,pin,gpio.BOTH_EDGES,gpio.SET_PULL_UP)
        gpio.gpio_claim_input(handle,13,gpio.SET_PULL_UP)
        self.levels = {p:gpio.gpio_read(handle,p) for p in (5,6)}
        self.decoder = Decoder((self.levels[5]<<1)|self.levels[6])
        self.raw = self.stable = gpio.gpio_read(handle,13)
        self.changed = None
        self.armed = self.stable == 1
        for pin in (5,6):
            self.callbacks.append(gpio.callback(handle,pin,gpio.BOTH_EDGES,self.edge))

    def edge(self, chip, pin, level, tick):
        if level not in (0,1):
            return
        with self.lock:
            self.levels[pin] = level
            action = self.decoder.update((self.levels[5]<<1)|self.levels[6])
            if action:
                self.events.append(action)

    def poll(self, now):
        raw = self.gpio.gpio_read(self.handle,13)
        if raw != self.raw:
            self.raw, self.changed = raw, now
        click = False
        if self.changed is not None and now-self.changed >= 0.035 and raw != self.stable:
            self.stable = raw
            if raw:
                self.armed = True
            elif self.armed:
                click, self.armed = True, False
        with self.lock:
            actions = list(self.events)
            self.events.clear()
        if click:
            actions.append('ENTER')
        return actions

    def close(self):
        for callback in self.callbacks:
            callback.cancel()
