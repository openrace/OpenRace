import logging

class Emitter:
    def __init__(self):
        self.listeners = []

    def connect(self, listener):
        self.listeners.append(listener)

    def emit(self, *args, **kwargs):
        for l in self.listeners:
            l(*args, **kwargs)


