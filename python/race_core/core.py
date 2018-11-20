#!/usr/bin/env python
# vim: set filencoding=utf-8

import logging
import time
import os
import click

from .handlers.racetracker import LapRFRaceTracker

myPath = os.path.dirname(os.path.realpath(__file__))
logPath = os.path.join(myPath, "log/race_core.log")
logging.basicConfig(
    # filename=logPath,
    format="%(asctime)s %(levelname)-7s %(message)s",
    datefmt="%Y-%d-%m %H:%M:%S",
    level=logging.DEBUG,
)


@click.command()
@click.option('--device', prompt='Device?', default="/dev/ttyACM0")
def main(device):
    logging.info("starting up")

    tracker = LapRFRaceTracker(device)
    tracker.on_version.connect(logging.info)

    tracker.request_version()

    tracker.read_data(stop_if_no_data=True)


if __name__ == '__main__':
    main()
