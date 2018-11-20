#!/usr/bin/env python
# vim: set filencoding=utf-8

import logging
import serial
from ..common import Emitter


class SerialInterfaceHandler:
    def __init__(self, device):
        self.device = device
        self.serial = None
        self.data_available = Emitter()
        self.serial = serial.Serial(self.device, 115200, timeout=0)

    def read_data(self, stop_if_no_data=False):
        while True:
            readable_len = max(0, min(2048, self.serial.in_waiting))
            if stop_if_no_data and readable_len == 0:
                return
            elif readable_len == 0:
                readable_len = 1
            data = self.serial.read(readable_len)
            if len(data):
                self.data_available.emit(data)

    def send_data(self, data):
        logging.debug("sending data <%s>" % data)
        self.serial.write(data)
