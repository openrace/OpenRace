#!/usr/bin/env python
# vim: set filencoding=utf-8

import logging

from ..common import Emitter


class Pilot:
    def __init__(self, frequency, name=""):
        self.name = name
        self.frequency = frequency
        self.times = []


class RaceTracker:
    def __init__(self):
        pass

    def start_race(self):
        raise NotImplemented()

    def end_race(self):
        raise NotImplemented()

    def save_settings(self):
        raise NotImplemented()

    def get_settings(self):
        raise NotImplemented()

    def request_version(self):
        raise NotImplemented()


from .laprf import lapRFprotocol
from .serialinterface import SerialInterfaceHandler


def mklog(prefix, level):
    def logany(*args, **kwargs):
        call = getattr(logging, level)
        if kwargs:
            call("%s %s %s" % (prefix, str(args), str(kwargs)))
        else:
            call("%s %s" % (prefix, str(args)))

    return logany


class LapRFRaceTracker(RaceTracker):
    def __init__(self, device):
        super().__init__()
        self.device = device
        self.laprf = None
        self.serial_dev = None

        self.on_version = Emitter()

        self.serial_dev = SerialInterfaceHandler(self.device)


        self.laprf = lapRFprotocol(self.serial_dev)

        self.serial_dev.data_available.connect(self.laprf.receive_data)

        self.laprf.status_packet.connect(mklog('status_packet', 'debug'))
        self.laprf.rf_settings_packet.connect(mklog('rf_settings_packet', 'debug'))
        self.laprf.passing_packet.connect(mklog('passing_packet', 'debug'))

        self.laprf.factory_name_signal.connect(mklog('factory_name_signal', 'debug'))

        self.laprf.version_packet.connect(
            lambda version, _: self.on_version.emit(".".join([str(x) for x in version]))
        )

        self.laprf.time_sync_packet.connect(mklog('time_sync_packet', 'debug'))

    def request_version(self):
        self.send_data(self.laprf.request_version())

    def send_data(self, data):
        self.serial_dev.send_data(data)

    def read_data(self, stop_if_no_data=False):
        self.serial_dev.read_data(stop_if_no_data)

    # laprf.request_save_settings
    # laprf.request_shutdown
    # laprf.request_start_race
    # laprf.request_stop_race
    # laprf.request_data
    # laprf.request_version
    # laprf.request_time
