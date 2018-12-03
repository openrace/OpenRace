#!/usr/bin/env python
# vim: set filencoding=utf-8

import logging

from ..common import Emitter
from ..common import mklog
# from ..common import poilot


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

        self.on_passing_packet = Emitter()
        self.on_status_packet = Emitter()

        self.laprf.status_packet.connect(self.status_recieved)
        self.laprf.time_sync_packet.connect(self.time_sync)
        self.laprf.version_packet.connect(self.on_version_packet)
        self.laprf.rf_settings_packet.connect(self.rf_settings_packet)
        self.laprf.passing_packet.connect(self.pilot_passed)

        self.laprf.factory_name_signal.connect(mklog('factory_name_signal', 'debug'))

        self.millivolts = 0.0
        self.system_version = None
        self.protocol_version = None
        self.timedelta = 0

        self.serial_dev.send_data(self.laprf.request_version())
        self.serial_dev.send_data(self.laprf.request_time())

    def time_sync(self, last_time_request, time_rtc_time, rtc_time, packet_receive_time):
        packet_delta = packet_receive_time - last_time_request
        device_offset = (packet_receive_time + last_time_request) / 2.0 - rtc_time
        logging.info("Time stats: Packet delta: %s - Device offset: %s" % (packet_delta, device_offset))

    def on_version_packet(self, system_version, protocol_version):
        self.system_version = ".".join([str(x) for x in system_version])
        self.protocol_version = protocol_version
        logging.info("Systemversion: %s, Protocol version: %s" % (self.system_version, self.protocol_version))

    def send_data(self, data):
        self.serial_dev.send_data(data)

    def read_data(self, stop_if_no_data=False):
        self.serial_dev.read_data(stop_if_no_data)

    # Emitting methods
    def pilot_passed(
            self,
            decoder_id,
            detection_number,
            pilot_id,
            rtc_time,
            detection_peak_height,
            detection_flags):
        self.on_passing_packet(
            pilot_id = pilot_id,
            seconds = rtc_time / 1000000 - self.timedelta
        )
        # logging.debug("Passing packet:")
        # logging.debug("decoder_id:            %s" % decoder_id)
        # logging.debug("detection_number:      %s" % detection_number)
        # logging.debug("pilot_id:              %s" % pilot_id)
        # logging.debug("rtc_time:              %s" % rtc_time)
        # logging.debug("detection_peak_height: %s" % detection_peak_height)
        # logging.debug("detection_flags:       %s" % detection_flags)

    def rf_settings_packet(self, pilot):
        # answer to request_pilot
        logging.debug("Pilot: %s " % pilot)

    def status_recieved(self, status_count, millivolts, rssis):
        self.millivolts = millivolts
        self.on_status_packet(rssis = rssis)

    # Setting Methods
    def set_pilot(self, id, band, freq, gain, channel, enabled, threshold):
        logging.info("Setting pilot")

        data = []
        data.append(self.laprf.build_FOR("PILOT_ID", id))
        data.append(self.laprf.build_FOR("RF_BAND", band))
        data.append(self.laprf.build_FOR("RF_FREQUENCY", freq))
        data.append(self.laprf.build_FOR("RF_GAIN", gain))
        data.append(self.laprf.build_FOR("RF_CHANNEL", channel))
        data.append(self.laprf.build_FOR("RF_ENABLE", enabled))
        data.append(self.laprf.build_FOR("RF_THRESHOLD", threshold))
        packet = self.laprf.build_header_and_data_packet("RF_SETTINGS", b"".join(data))
        self.send_data(packet)

    def request_pilot(self, pilot_id):
        logging.debug("Requesting pilot %s" % pilot_id)
        data = self.laprf.build_FOR("PILOT_ID", pilot_id)
        packet = self.laprf.build_header_and_data_packet("RF_SETTINGS", data)
        self.send_data(packet)

    def request_start_race(self):
        logging.info("Request race start")
        self.laprf.request_start_race()

    def request_stop_race(self):
        logging.info("Request race stop")
        self.laprf.request_stop_race()

    # laprf.request_save_settings
    # laprf.request_shutdown
    # laprf.request_start_race
    # laprf.request_stop_race
    # laprf.request_data
    # laprf.request_version
    # laprf.request_time
