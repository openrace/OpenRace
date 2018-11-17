#!/usr/bin/env python
# vim: set filencoding=utf-8

import protocols
import handlers
import logging
import time
import os

myPath = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../')
logPath = os.path.join(myPath, 'src/log/race_core.log')
logging.basicConfig(
    filename=logPath,
    format='%(asctime)s %(levelname)-7s %(message)s',
    datefmt='%Y-%d-%m %H:%M:%S',
    level=logging.DEBUG)

if __name__ == "__main__":
    logging.info("starting up")
    cih = handlers.serialinterface.SerialInterfaceHandler('/dev/ttyACM0')
    laprf = protocols.laprf.lapRFprotocol(cih)

    emi = protocols.laprf.Emitter()
    emi.connect(logging.info)

    # hacking begins

    # requesting version
    cih.send_data(laprf.request_version())

    while True:
        # read data loop
        laprf.receive_data(cih.readline())

        # just so we can kill it
        time.sleep(0.01)


    # laprf.receive_data
    # laprf.request_save_settings
    # laprf.request_shutdown
    # laprf.request_start_race
    # laprf.request_stop_race
    # laprf.request_data
    # laprf.request_version
    # laprf.request_time
