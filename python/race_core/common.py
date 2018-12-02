import logging


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
    def __init__(self, frequency, name=""):
        self.name = name
        self.frequency = frequency
        self.laps = []
