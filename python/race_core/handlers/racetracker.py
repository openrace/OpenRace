#!/usr/bin/env python
# vim: set filencoding=utf-8

import logging


class Pilot:
    def __init__(self, frequency, name=""):
        self.name = name
        self.frequency = frequency
        self.times = []


class RaceTracker:

    def __init__(self):
        self.callbacks = []
        self.initialize()

    def initialize(self):
        logging.debug("initializing")
        pass

    def start_race(self):
        logging.debug("start race")
        pass

    def end_race(self):
        logging.debug("end race")
        pass

    def save_settings(self):
        logging.debug("save setting")
        pass

    def get_settings(self):
        logging.debug("get setting")
        pass

    def version(self):
        logging.debug("request version")
        pass

    def register_callback(self, callback):
        self.callbacks.append(callback)


from .laprf import lapRFprotocol
from .serialinterface import SerialInterfaceHandler


class LapRFRaceTracker(RaceTracker):

    def __init__(self, device, return_callback):
        self.device = device
        self.laprf = None
        self.serial_dev = None
        self.return_callback = return_callback
        RaceTracker.__init__(self)

    def initialize(self):
        RaceTracker.initialize(self)
        self.serial_dev = SerialInterfaceHandler(self.device)
        self.laprf = lapRFprotocol(self.serial_dev, self.return_callback)

    def version(self):
        RaceTracker.version(self)
        self.send_data(self.laprf.request_version())

    def send_data(self, data):
        self.serial_dev.send_data(data)

    def recieve_data(self):
        self.laprf.receive_data(self.serial_dev.readline())

    # laprf.request_save_settings
    # laprf.request_shutdown
    # laprf.request_start_race
    # laprf.request_stop_race
    # laprf.request_data
    # laprf.request_version
    # laprf.request_time