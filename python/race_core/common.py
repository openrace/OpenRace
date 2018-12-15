import logging
import time

class Emitter:
    def __init__(self):
        self.listeners = []

    def connect(self, listener):
        self.listeners.append(listener)

    def emit(self, *args, **kwargs):
        for l in self.listeners:
            l(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        self.emit(*args, **kwargs)


def mklog(prefix, level):
    def logany(*args, **kwargs):
        call = getattr(logging, level)
        if kwargs:
            call("%s %s %s" % (prefix, str(args), str(kwargs)))
        else:
            call("%s %s" % (prefix, str(args)))

    return logany


class Pilot:
    def __init__(self, frequency = 0, name = "Unknown"):
        self.name = name
        self.frequency = frequency
        self.laps = []
        self.enabled = False
        self.lastlap = 0

    def show(self):
        if self.enabled:
            state = "Enabled"
        else:
            state = "Disabled"
        if self.name:
            return "MHz: %s; Name: %s; %s" % (self.frequency, self.name, state)
        else:
            return "MHz: %s; %s" % (self.frequency, state)

    def passed(self):
        now = time.time()
        if self.lastlap + 10 < now:
            self.lastlap = now
            self.laps.append(now)
            return True
        return False

    def get_stats(self):
        ret = {}
        ret['name'] = self.name
        ret['laps'] = self.laps
        return ret
