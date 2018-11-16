#!/usr/bin/env python
# vim: set filencoding=utf-8

import logging
import serial


class SerialInterfaceHandler:
    def __init__(self, device = None):
        self.device = device
        self.buf = bytearray()
        self.serial = None

        if self.device:
            self.open_device()

    def open_device(self):
        logging.info("opening serial device %s" % (self.device))
        self.serial = serial.Serial(self.device, 115200, timeout=0)

    def readline(self):
        i = self.buf.find(b"\n")
        if i >= 0:
            r = self.buf[:i + 1]
            self.buf = self.buf[i + 1:]
            return r
        while True:
            i = max(1, min(2048, self.serial.in_waiting))
            data = self.serial.read(i)
            i = data.find(b"\n")
            if i >= 0:
                r = self.buf + data[:i + 1]
                self.buf[0:] = data[i + 1:]
                return r
            else:
                self.buf.extend(data)

    def send_data(self, data):
        self.serial.write(data)
