#!/usr/bin/env python
# vim: set filencoding=utf-8

import struct
import time
import tempfile
import logging


class FOR_values():
    def __init__(self, tof, length, data_type):
        self.tof = tof
        self.length = length
        self.data_type = data_type


FOR_constants = {
    'PILOT_ID': FOR_values(0x01, 0x01, 'B'),
    'RTC_TIME': FOR_values(0x02, 0x08, 'q'),
    'STATUS_FLAGS': FOR_values(0x03, 0x02, 'H'),
    'DECODER_ID': FOR_values(0x20, 0x04, 'i'),
    'DETECTION_NUMBER': FOR_values(0x21, 0x04, 'i'),
    'DETECTION_PEAK_HEIGHT': FOR_values(0x22, 0x02, 'H'),
    'DETECTION_FLAGS': FOR_values(0x23, 0x02, 'H'),
    'STATUS_NOISE': FOR_values(0x20, 0x02, 'H'),
    'STATUS_INPUT_VOLTAGE': FOR_values(0x21, 0x02, 'H'),
    'STATUS_RSSI': FOR_values(0x22, 0x04, 'f'),
    'STATUS_GATE_STATE': FOR_values(0x23, 0x01, 'B'),
    'STATUS_COUNT': FOR_values(0x24, 0x04, 'i'),
    'RSSI_MIN': FOR_values(0x20, 0x04, 'f'),
    'RSSI_MAX': FOR_values(0x21, 0x04, 'f'),
    'RSSI_MEAN': FOR_values(0x22, 0x04, 'f'),
    'RSSI_COUNT': FOR_values(0x23, 0x04, 'i'),
    'RSSI_ENABLE': FOR_values(0x24, 0x01, 'B'),
    'RSSI_INTERVAL': FOR_values(0x25, 0x01, 'B'),
    'RSSI_SDEV': FOR_values(0x26, 0x04, 'f'),
    'DETECTION_COUNT_CURRENT': FOR_values(0x20, 0x04, 'i'),
    'DETECTION_COUNT_FROM': FOR_values(0x21, 0x04, 'i'),
    'DETECTION_COUNT_UNTIL': FOR_values(0x22, 0x04, 'i'),
    'RF_ENABLE': FOR_values(0x20, 0x02, 'H'),
    'RF_CHANNEL': FOR_values(0x21, 0x02, 'H'),
    'RF_BAND': FOR_values(0x22, 0x02, 'H'),
    'RF_THRESHOLD': FOR_values(0x23, 0x04, 'f'),
    'RF_GAIN': FOR_values(0x24, 0x02, 'H'),
    'RF_FREQUENCY': FOR_values(0x25, 0x02, 'H'),
    'TIME_RTC_TIME': FOR_values(0x20, 0x08, 'q'),
    'CTRL_REQ_RACE': FOR_values(0x20, 0x01, 'B'),
    'CTRL_REQ_CAL': FOR_values(0x21, 0x01, 'B'),
    'CTRL_REQ_DATA': FOR_values(0x22, 0x04, 'i'),
    'CTRL_REQ_STATIC_CAL': FOR_values(0x23, 0x01, 'B'),
    'DATA_DUMP': FOR_values(0x20, 0x00, 's'),
    'DATA_DUMP_LAST_PACKET': FOR_values(0x21, 0x00, 's'),
    'CALIBRATION_LOG_HEIGHT': FOR_values(0x20, 0x04, 'f'),
    'CALIBRATION_LOG_NUM_PEAK': FOR_values(0x21, 0x02, 'H'),
    'CALIBRATION_LOG_BASE': FOR_values(0x22, 0x02, 'H'),
    'SETTINGS_NAME': FOR_values(0x20, 0x0A, '10s'),
    'SETTINGS_STATUS_UPDATE_PERIOD': FOR_values(0x22, 0x02, 'H'),
    'SETTINGS_RSSI_SAMPLE_PERIOD': FOR_values(0x23, 0x04, 'i'),
    'SETTINGS_FACTORY_NAME': FOR_values(0x24, 0x0A, '10s'),
    'SETTINGS_SAVE_SETTINGS': FOR_values(0x25, 0x01, 'B'),
    'SETTINGS_MIN_LAP_TIME': FOR_values(0x26, 0x04, 'i'),
    'SETTINGS_ENABLED_MODULES': FOR_values(0x27, 0x01, 'B'),
    'DESC_SYSTEM_VERSION': FOR_values(0x20, 0x04, 'i'),
    'DESC_PROTOCOL_VERSION': FOR_values(0x21, 0x01, 'B'),
    'NETWORK_PING': FOR_values(0x20, 0x04, 'i'),
}

TOR_constants = {
    'RSSI': 0xDA01,
    'RF_SETTINGS': 0xDA02,
    'STATE_CTRL': 0xDA04,
    'DATA': 0xDA05,
    'CALIBRATION_LOG': 0xDA06,
    'SETTINGS': 0xDA07,
    'DESC': 0xDA08,
    'DETECTION': 0xDA09,
    'STATUS': 0xDA0A,
    'RESEND': 0xDA0B,
    'TIME': 0xDA0C,
    'NETWORK': 0xDA0D
}


class Emitter:
    def __init__(self):
        self.listeners = []

    def connect(self, listener):
        logging.debug("connecting listener")
        self.listeners.append(listener)

    def emit(self, *args, **kwargs):
        logging.debug("emitting...")
        for l in self.listeners:
            l(*args, **kwargs)


def return_tester(*args, **kwargs):
    logging.info("return tester called")

    for arg in args:
        logging.info(arg)

    for key, value in kwargs.items():
        logging.info("%s == %s" % (key, value))


class lapRFprotocol:

    def __init__(self, communication_interface=None):
        self.status_packet = Emitter()
        self.rf_settings_packet = Emitter()
        self.passing_packet = Emitter()
        self.passing_packet.connect(return_tester)

        self.factory_name_signal = Emitter()
        self.version_packet = Emitter()
        self.time_sync_packet = Emitter()

        self.crc16_table = []
        self.init_crc16_table()

        self.communication_interface = communication_interface

        self.laprf_buffer = []
        self.laprf_parsing_status = 'LOOK_FOR_SOR'
        self.laprf_receive_count = 0

        self.received_packets_count = 0

        self.SOR = 0x5a
        self.EOR = 0x5b
        self.ESC = 0x5c
        self.escape_offset = 0x40

        self.last_time_request = 0

        self.receiving_data = False
        self.data_file = None

        self.status_count = 0
        logging.debug("proto init")
        crc_check_str = ['1', '2', '3', '4', '5', '6', '7', '8', '9']
        crc_check_val = bytearray("123456789", encoding="ascii")
        logging.debug("crc check: {:04x}".format(self.compute_CRC(crc_check_val)))

        self.logging = False

    def log(self, txt, end='\n'):
        if self.logging:
            logging.debug(txt, end=end)

    def receive_data(self, data):
        for d in data:
            if self.laprf_protocol_parser(d):
                self.laprf_protocol_decoder(self.laprf_buffer)
                self.laprf_buffer = []

    # lapRF helper functions
    def build_FOR(self, field_type, data):
        tof = FOR_constants[field_type].tof
        length = FOR_constants[field_type].length
        data_type = FOR_constants[field_type].data_type

        if data == None:
            packed = struct.pack('<BB', tof, 0)
        else:
            packed = struct.pack('<BB' + data_type, tof, length, data)

        # logging.debug("packed FOR [{}]".format(packed))
        return packed

    def init_crc16_table(self):

        for i in range(256):
            remainder = (i << 8) & 0xff00
            #            crc = (i << 8) & 0xffff

            for j in range(8):
                if remainder & 0x8000 == 0x8000:
                    remainder = ((remainder << 1) & 0xFFFF) ^ 0x8005
                else:
                    remainder = ((remainder << 1) & 0xFFFF)

            self.crc16_table.append(remainder)

    #        logging.debug( crc16_table )
    #        logging.debug("crc16 table length" , len(crc16_table))

    def reflect(self, input, nbits):
        output = 0

        for i in range(nbits):
            if (input & 0x01) == 0x01:
                output |= (1 << ((nbits - 1) - i))

            input = input >> 1

        return output

    def compute_CRC(self, data):
        crc = 0x0000
        #    logging.debug (type(data))
        for bt in data:
            a = self.reflect(bt, 8) & 0xFF
            b = ((crc >> 8) & 0xFF)
            c = ((crc << 8) & 0xFFFF)
            dat = a ^ b
            crc = self.crc16_table[dat] ^ c

        return self.reflect(crc, 16)

    def escape_packet(self, packet):
        out = [packet[0]]
        #    logging.debug(packet)
        for b in packet[1:-1]:
            #        logging.debug(b)
            if b == self.SOR or b == self.EOR or b == self.ESC:
                out.append(self.ESC)
                out.append(b + self.escape_offset)
            else:
                out.append(b)

        out.append(self.EOR)
        #    logging.debug(out)
        #    logging.debug("packet conversion")
        bta = bytes(out)
        #    logging.debug(bytes(out))
        #    return bytes(out)
        #    logging.debug(type(bta))
        #    logging.debug("packet done")
        return bta

    # return out

    def build_header_and_data_packet(self, type_of_record, data):
        # header
        SOR = self.SOR
        version = 0x01
        length = 0
        header_length = 7
        stop_symbol_len = 1
        if data is not None:
            length = len(data) + header_length + stop_symbol_len  # 2 bytes, lsb first
        else:
            length = header_length + stop_symbol_len

        CRC = 0x0000  # 2 bytes LSB first

        TOR = TOR_constants[type_of_record]

        EOR = self.EOR

        header = struct.pack('<BHHH', SOR, length, CRC, TOR)

        #    logging.debug(type(header))
        end = struct.pack('<B', EOR)
        #    logging.debug( type(data) )
        #    logging.debug(type(end))
        packet = None
        if data is not None:
            packet = header + data + end
        else:
            packet = header + end

        CRC = self.compute_CRC(packet)
        #    logging.debug(CRC)

        header = struct.pack('<BHHH', SOR, length, CRC, TOR)

        packet = None
        if data is not None:
            packet = header + data + end
        else:
            packet = header + end

        #    logging.debug("escaping")
        packet2 = self.escape_packet(packet)
        #    logging.debug("escaped")
        #    logging.debug(type(packet2))

        return packet2

    def laprf_protocol_parser(self, rx):
        # parse
        #        logging.debug("received: [", hex(rx), "] - status ", self.laprf_parsing_status)
        rx_val = int(rx)
        if self.laprf_parsing_status == 'LOOK_FOR_SOR':
            if rx_val == self.SOR:
                self.laprf_buffer = [rx]
                self.laprf_receive_count += 1
            self.laprf_parsing_status = 'LOOK_FOR_EOR'

        elif self.laprf_parsing_status == 'ESCAPE':
            self.laprf_buffer.append(rx - self.escape_offset)

            self.laprf_receive_count += 1

            self.laprf_parsing_status = 'LOOK_FOR_EOR'

        elif self.laprf_parsing_status == 'LOOK_FOR_EOR':
            if rx_val == self.ESC:
                self.laprf_parsing_status = 'ESCAPE'
            elif rx_val == self.EOR:
                self.laprf_buffer.append(rx)
                self.laprf_receive_count += 1
                self.laprf_parsing_status = 'LOOK_FOR_SOR'

                return True
            else:
                self.laprf_buffer.append(rx)
                self.laprf_receive_count += 1

        return False

    def request_save_settings(self):
        logging.info("REQUEST SAVE")
        data = self.build_FOR('SETTINGS_SAVE_SETTINGS', 1)
        packet = self.build_header_and_data_packet('SETTINGS', data)
        return packet

    def request_shutdown(self):
        logging.info("REQUEST SHUTDOWN")
        data = self.build_FOR('CTRL_REQ_RACE', 0xFF)
        packet = self.build_header_and_data_packet('STATE_CTRL', data)
        return packet

    def request_start_race(self):
        logging.info("REQUEST START RACE")
        data = self.build_FOR('CTRL_REQ_RACE', 1)
        packet = self.build_header_and_data_packet('STATE_CTRL', data)
        return packet

    def request_stop_race(self):
        logging.info("REQUEST STOP RACE")
        data = self.build_FOR('CTRL_REQ_RACE', 0)
        packet = self.build_header_and_data_packet('STATE_CTRL', data)
        return packet

    def request_data(self):
        logging.info("REQUEST DATA")
        data = self.build_FOR('CTRL_REQ_DATA', 0)
        packet = self.build_header_and_data_packet('STATE_CTRL', data)
        return packet

    def request_version(self):
        logging.info("REQUEST VERSION")
        data = self.build_FOR('DESC_SYSTEM_VERSION', None)
        packet = self.build_header_and_data_packet('DESC', data)
        return packet

    def request_time(self):
        now = time.time()
        self.last_time_request = now
        logging.info("[{}] REQUEST TIME".format(now))
        data = self.build_FOR('RTC_TIME', None)
        packet = self.build_header_and_data_packet('TIME', data)
        return packet

    def laprf_protocol_decoder(self, packet):

        #        logging.debug(type(packet))

        header = bytes(packet[0:7])

        #        header = packet[0:10]
        #        logging.debug(type(header))
        #        logging.debug("header:", len(header))
        #        logging.debug("header:", header)
        self.received_packets_count += 1
        self.log("packet count: {}".format(self.received_packets_count))
        packet_receive_time = time.time()
        self.log("[{}] ".format(packet_receive_time), end=' ')
        SOR, length, CRC, TOR = struct.unpack('<BHHH', header)
        if len(packet) != length:
            self.log("length error")
        else:
            self.log(" length OK ", end=' ')
        # set CRC to 0
        packet[3] = 0
        packet[4] = 0
        computed_crc = self.compute_CRC(bytearray(packet))
        #        computed_crc = CRC
        if computed_crc != CRC:
            self.log("CRC error, computed: {:04x} received {:04x}".format(computed_crc, CRC))
            return
        else:
            self.log(" CRC OK ", end=' ')

        if TOR == TOR_constants['DETECTION']:
            # passing record

            # logging.debug( " [ ", end=' ')
            #
            # for d in packet:
            #     logging.debug( hex(d), end=' ')
            # logging.debug()

            self.log(" passing ", end=' ')
            idx = 7
            decoder_id = 0
            detection_number = 0
            detection_peak_height = 0
            detection_flags = 0
            pilot_id = 0
            rtc_time = 0

            while int(packet[idx]) != self.EOR:

                field_str_idx = ''

                if int(packet[idx]) == FOR_constants['DECODER_ID'].tof:
                    idx += 1
                    field_str_idx = 'DECODER_ID'
                elif int(packet[idx]) == FOR_constants['PILOT_ID'].tof:
                    idx += 1
                    field_str_idx = 'PILOT_ID'
                elif int(packet[idx]) == FOR_constants['RTC_TIME'].tof:
                    idx += 1
                    field_str_idx = 'RTC_TIME'
                elif int(packet[idx]) == FOR_constants['DETECTION_NUMBER'].tof:
                    idx += 1
                    field_str_idx = 'DETECTION_NUMBER'
                elif int(packet[idx]) == FOR_constants['DETECTION_PEAK_HEIGHT'].tof:
                    idx += 1
                    field_str_idx = 'DETECTION_PEAK_HEIGHT'
                elif int(packet[idx]) == FOR_constants['DETECTION_FLAGS'].tof:
                    idx += 1
                    field_str_idx = 'DETECTION_FLAGS'
                else:
                    logging.warning("UNKNOWN FIELD ID: {}".format(packet[idx]), end=' ')
                    idx += 1

                if field_str_idx != '':
                    length = FOR_constants[field_str_idx].length
                    data_type = FOR_constants[field_str_idx].data_type
                    length += 1  # add size byte
                    size, data = struct.unpack('<B' + data_type, bytes(packet[idx:idx + length]))
                    idx += length

                    self.log("{} - [{}]:\t{}".format(field_str_idx, size, data))

                    if field_str_idx == 'PILOT_ID':
                        pilot_id = data
                    elif field_str_idx == 'DECODER_ID':
                        decoder_id = data
                    elif field_str_idx == 'RTC_TIME':
                        rtc_time = data
                    elif field_str_idx == 'DETECTION_NUMBER':
                        detection_number = data
                    elif field_str_idx == 'DETECTION_PEAK_HEIGHT':
                        detection_peak_height = data
                    elif field_str_idx == 'DETECTION_FLAGS':
                        detection_flags = data

            rtc_time = 0
            #            logging.debug("[" + str((decoder_id, passing_number, transponder, rtc_time,
            #            passing_strength, passing_hits, passing_flags)) + "]")

            self.passing_packet.emit(decoder_id, detection_number, pilot_id, rtc_time, detection_peak_height,
                                     detection_flags)

        elif TOR == TOR_constants['RF_SETTINGS']:
            self.log(" RF settings ", end=' ')
            idx = 7
            data = object()
            max_pilots = 8
            rf_pilotid = -1
            rf_enable = -1
            rf_channel = -1
            rf_band = -1
            rf_gain = -1
            rf_thr = -1
            rf_freq = -1

            lst = []
            dct = None
            while int(packet[idx]) != self.EOR:
                field_str_idx = ''

                #                logging.debug(hex(int(packet[idx])), end=' ')
                if int(packet[idx]) == FOR_constants['PILOT_ID'].tof:
                    idx += 1
                    field_str_idx = 'PILOT_ID'
                elif int(packet[idx]) == FOR_constants['RF_GAIN'].tof:
                    idx += 1
                    field_str_idx = 'RF_GAIN'
                elif int(packet[idx]) == FOR_constants['RF_THRESHOLD'].tof:
                    idx += 1
                    field_str_idx = 'RF_THRESHOLD'
                elif int(packet[idx]) == FOR_constants['RF_ENABLE'].tof:
                    idx += 1
                    field_str_idx = 'RF_ENABLE'
                elif int(packet[idx]) == FOR_constants['RF_CHANNEL'].tof:
                    idx += 1
                    field_str_idx = 'RF_CHANNEL'
                elif int(packet[idx]) == FOR_constants['RF_BAND'].tof:
                    idx += 1
                    field_str_idx = 'RF_BAND'
                elif int(packet[idx]) == FOR_constants['RF_FREQUENCY'].tof:
                    idx += 1
                    field_str_idx = 'RF_FREQUENCY'
                else:
                    logging.warning("UNKNOWN FIELD ID: {}".format(packet[idx]), end=' ')
                    idx += 1

                if field_str_idx != '':

                    length = FOR_constants[field_str_idx].length
                    data_type = FOR_constants[field_str_idx].data_type
                    length += 1  # add size byte
                    size, data = struct.unpack('<B' + data_type, bytes(packet[idx:idx + length]))
                    idx += length

                    if field_str_idx == 'PILOT_ID':
                        rf_pilotid = data - 1
                        dct = {'PILOT_ID': data}

                        lst.append(dct)

                    elif field_str_idx == 'RF_GAIN' or field_str_idx == 'RF_THRESHOLD' or field_str_idx == 'RF_ENABLE' or field_str_idx == 'RF_CHANNEL' or field_str_idx == 'RF_BAND' or field_str_idx == 'RF_FREQUENCY':
                        if rf_pilotid > -1 and rf_pilotid < max_pilots:
                            dct[field_str_idx] = data

                    self.log("{} - [{}]:\t{}".format(field_str_idx, size, data), end=' ')

            self.log('\n')

            self.log(lst)

            self.rf_settings_packet.emit(lst)

        elif TOR == TOR_constants['STATUS']:
            self.log(" status ", end=' ')
            self.status_count += 1

            idx = 7
            rssis = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
            current_pilot_id = 0
            while int(packet[idx]) != self.EOR:

                field_str_idx = ''
                if int(packet[idx]) == FOR_constants['STATUS_NOISE'].tof:  # noise
                    idx += 1
                    field_str_idx = 'STATUS_NOISE'

                elif int(packet[idx]) == FOR_constants['STATUS_INPUT_VOLTAGE'].tof:  # noise
                    idx += 1
                    field_str_idx = 'STATUS_INPUT_VOLTAGE'
                elif int(packet[idx]) == FOR_constants['PILOT_ID'].tof:  # noise
                    idx += 1
                    field_str_idx = 'PILOT_ID'
                elif int(packet[idx]) == FOR_constants['RSSI_MEAN'].tof:  # noise
                    idx += 1
                    field_str_idx = 'RSSI_MEAN'
                elif int(packet[idx]) == FOR_constants['STATUS_COUNT'].tof:  # noise
                    idx += 1
                    field_str_idx = 'STATUS_COUNT'
                elif int(packet[idx]) == FOR_constants['STATUS_GATE_STATE'].tof:  # noise
                    idx += 1
                    field_str_idx = 'STATUS_GATE_STATE'
                elif int(packet[idx]) == FOR_constants['STATUS_FLAGS'].tof:  # noise
                    idx += 1
                    field_str_idx = 'STATUS_FLAGS'
                else:
                    idx += 1

                if field_str_idx != '':
                    length = FOR_constants[field_str_idx].length
                    data_type = FOR_constants[field_str_idx].data_type
                    length += 1  # add size byte
                    size, data = struct.unpack('<B' + data_type, bytes(packet[idx:idx + length]))
                    idx += length

                    self.log("{} - [{}]:\t{}".format(field_str_idx, size, data))

                    if field_str_idx == 'PILOT_ID':
                        current_pilot_id = data
                    elif field_str_idx == 'RSSI_MEAN':
                        rssis[current_pilot_id - 1] = data

            self.status_packet.emit(self.status_count, rssis)
        elif TOR == TOR_constants['DESC']:
            self.log(" desc ", end=' ')
            idx = 7
            system_version = [0, 0, 0, 0]
            protocol_version = 0

            while int(packet[idx]) != self.EOR:

                field_str_idx = ''
                if int(packet[idx]) == FOR_constants['DESC_SYSTEM_VERSION'].tof:
                    idx += 1
                    field_str_idx = 'DESC_SYSTEM_VERSION'
                elif int(packet[idx]) == FOR_constants['DESC_PROTOCOL_VERSION'].tof:
                    idx += 1
                    field_str_idx = 'DESC_PROTOCOL_VERSION'
                else:
                    idx += 1

                if field_str_idx != '':
                    length = FOR_constants[field_str_idx].length
                    data_type = FOR_constants[field_str_idx].data_type
                    length += 1  # add size byte
                    size, data = struct.unpack('<B' + data_type, bytes(packet[idx:idx + length]))
                    idx += length

                    self.log("{} - [{}]:\t{}".format(field_str_idx, size, data))

                    if field_str_idx == 'DESC_SYSTEM_VERSION':
                        system_version = [(data >> 24) & 0xFF,
                                          (data >> 16) & 0xFF,
                                          (data >> 8) & 0xFF,
                                          (data >> 0) & 0xFF, ]
                    elif field_str_idx == 'DESC_PROTOCOL_VERSION':
                        protocol_version = data

            self.version_packet.emit(system_version, protocol_version)

        elif TOR == TOR_constants['TIME']:
            rtc_time = 0
            time_rtc_time = 0
            self.log(" time ", end=' ')
            idx = 7
            while int(packet[idx]) != self.EOR:

                field_str_idx = ''
                if int(packet[idx]) == FOR_constants['TIME_RTC_TIME'].tof:
                    idx += 1
                    field_str_idx = 'TIME_RTC_TIME'
                    self.log("t")
                elif int(packet[idx]) == FOR_constants['RTC_TIME'].tof:
                    idx += 1
                    field_str_idx = 'RTC_TIME'
                    self.log("t")
                else:
                    idx += 1

                if field_str_idx != '':
                    length = FOR_constants[field_str_idx].length
                    data_type = FOR_constants[field_str_idx].data_type
                    length += 1  # add size byte
                    size, data = struct.unpack('<B' + data_type, bytes(packet[idx:idx + length]))
                    idx += length

                    if field_str_idx == 'RTC_TIME':  # device packet sendout time
                        self.log("rtc time: {}".format(data))
                        rtc_time = data * 1e-6
                    elif field_str_idx == 'TIME_RTC_TIME':  # device packet receive time
                        self.log("time rtc time: {}".format(data))
                        # self.factory_name_signal.emit(data)
                        time_rtc_time = data * 1e-6
            self.log("Packet delta: {}".format(packet_receive_time - self.last_time_request))
            self.log("Device offset: {}".format((packet_receive_time + self.last_time_request) / 2.0 - rtc_time))

            self.time_sync_packet.emit(self.last_time_request, time_rtc_time, rtc_time, packet_receive_time)

        elif TOR == TOR_constants['SETTINGS']:
            self.log(" settings packet ", end=' ')
            idx = 7
            while int(packet[idx]) != self.EOR:

                field_str_idx = ''
                if int(packet[idx]) == FOR_constants['SETTINGS_FACTORY_NAME'].tof:
                    idx += 1
                    field_str_idx = 'SETTINGS_FACTORY_NAME'
                    self.log("f")
                else:
                    idx += 1

                if field_str_idx != '':
                    length = FOR_constants[field_str_idx].length
                    data_type = FOR_constants[field_str_idx].data_type
                    length += 1  # add size byte
                    size, data = struct.unpack('<B' + data_type, bytes(packet[idx:idx + length]))
                    idx += length

                    if field_str_idx == 'SETTINGS_FACTORY_NAME':
                        self.factory_name_signal.emit(data)

        elif TOR == TOR_constants['NETWORK']:
            self.log(" network packet ", end=' ')

            idx = 7
            ping_number = 0

            while int(packet[idx]) != self.EOR:

                self.log(idx)
                field_str_idx = ''
                if int(packet[idx]) == FOR_constants['NETWORK_PING'].tof:  # noise
                    idx += 1
                    field_str_idx = 'NETWORK_PING'
                    self.log("f")
                else:
                    idx += 1

                if field_str_idx != '':
                    length = FOR_constants[field_str_idx].length
                    data_type = FOR_constants[field_str_idx].data_type
                    length += 1  # add size byte
                    size, data = struct.unpack('<B' + data_type, bytes(packet[idx:idx + length]))
                    idx += length

                    self.log("{} - [{}]: {}\t".format(field_str_idx, size, data))

                    ping_number = data

            self.log("ping: {}".format(ping_number))
        elif TOR == TOR_constants['DATA']:
            logging.debug("DATA", end='\n')

            idx = 7
            logging.info("data received: [{0}]: {1}".format(idx, hex(packet[idx]), end='\n'))

            tof = int(packet[idx])
            idx += 1
            sz = 5
            size, packet_idx = struct.unpack('<BI', bytes(packet[idx:idx + sz]))
            idx += sz
            logging.debug("data packet idx {0}, {1} bytes".format(packet_idx, size), end='\n')

            if size == 0:
                if self.receiving_data == True:
                    self.receiving_data = False
                    self.data_file.close()
                    logging.info("closing log data file", end='\n')
            else:
                if self.receiving_data == False:
                    self.receiving_data = True
                    self.data_file = tempfile.TemporaryFile()
                    logging.info("start data dump", end='\n')

                data = struct.unpack('<' + str(size) + 'B', bytes(packet[idx:idx + size]))
                idx += size
                self.data_file.write(bytearray(data))

                if tof == FOR_constants['DATA_DUMP_LAST_PACKET'].tof:
                    self.receiving_data = False
                    self.data_file.close()
                    logging.info("closing log data file", end='\n')
                    # ask to delete current one and start to send new one
                    # dt = self.build_FOR('CTRL_REQ_DATA', -1)
                    # packet = self.build_header_and_data_packet('STATE_CTRL', dt)
                    # self.communication_interface.send_data(packet)
                elif tof == FOR_constants['DATA_DUMP'].tof:
                    dt = self.build_FOR('CTRL_REQ_DATA', packet_idx + 1)
                    packet = self.build_header_and_data_packet('STATE_CTRL', dt)
                    self.communication_interface.send_data(packet)

        self.log("end receive")
