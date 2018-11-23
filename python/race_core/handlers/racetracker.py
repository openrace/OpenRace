#!/usr/bin/env python
# vim: set filencoding=utf-8

import logging

from ..common import Emitter
from ..common import mklog


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

    def pilot_passed(self):
        raise NotImplemented()
    #   decoder_id, detection_number, pilot_id, rtc_time, detection_peak_height, detection_flags,


from .laprf import lapRFprotocol
from .serialinterface import SerialInterfaceHandler


class LapRFRaceTracker(RaceTracker):
    def __init__(self, device):
        super().__init__()
        self.serial_dev = SerialInterfaceHandler(device)
        self.laprf = lapRFprotocol(self.serial_dev)
        self.serial_dev.data_available.connect(self.laprf.receive_data)

        self.on_version = Emitter()
        self.on_passing_packet= Emitter()

        self.laprf.status_packet.connect(mklog('status_packet', 'debug'))
        self.laprf.rf_settings_packet.connect(mklog('rf_settings_packet', 'debug'))
        self.laprf.factory_name_signal.connect(mklog('factory_name_signal', 'debug'))
        self.laprf.time_sync_packet.connect(mklog('time_sync_packet', 'debug'))
        # self.last_time_request, time_rtc_time, rtc_time, packet_receive_time

        self.laprf.version_packet.connect(
            # system_version, protocol_version
            lambda version, _: self.on_version.emit(".".join([str(x) for x in version]))
        )
        self.laprf.version_packet.connect(mklog('version_packet', 'debug'))
        # self.laprf.passing_packet.connect(self.pilot_passed)
        self.laprf.passing_packet.connect(mklog('passing_packet', 'debug'))


    def request_version(self):
        self.send_data(self.laprf.request_version())

    def request_time(self):
        self.send_data(self.laprf.request_time())

    def send_data(self, data):
        self.serial_dev.send_data(data)

    def read_data(self, stop_if_no_data=False):
        self.serial_dev.read_data(stop_if_no_data)

    # Emitting methods
    def pilot_passed(self):
        logging.debug("Passing packet:")
        logging.debug("decoder_id:            " % decoder_id)
        logging.debug("detection_number:      " % detection_number)
        logging.debug("pilot_id:              " % pilot_id)
        logging.debug("rtc_time:              " % rtc_time)
        logging.debug("detection_peak_height: " % detection_peak_height)
        logging.debug("detection_flags:       " % detection_flags)
        pass

    # laprf.request_save_settings
    # laprf.request_shutdown
    # laprf.request_start_race
    # laprf.request_stop_race
    # laprf.request_data
    # laprf.request_version
    # laprf.request_time
