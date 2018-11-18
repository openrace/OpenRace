#!/usr/bin/env python
# vim: set filencoding=utf-8

import logging
import time
import os

from handlers.racetracker import LapRFRaceTracker

myPath = os.path.dirname(os.path.realpath(__file__))
logPath = os.path.join(myPath, 'log/race_core.log')
logging.basicConfig(
    filename=logPath,
    format='%(asctime)s %(levelname)-7s %(message)s',
    datefmt='%Y-%d-%m %H:%M:%S',
    level=logging.DEBUG)


def return_tester(*args, **kwargs):
    logging.info("return tester called")

    for arg in args:
        logging.info(arg)

    for key, value in kwargs.items():
        logging.info("%s == %s" % (key, value))


if __name__ == "__main__":
    logging.info("starting up")

    tracker = LapRFRaceTracker('/dev/ttyACM0', return_tester)
    # tracker.register_callback()
    tracker.version()

    while True:
        logging.info("read data loop")
        tracker.recieve_data()

        # just so we can kill it
        time.sleep(0.01)
