#!/usr/bin/env python
# vim: set filencoding=utf-8

import logging
import os
import click
import paho.mqtt.client as mqtt

from .handlers.racetracker import LapRFRaceTracker

myPath = os.path.dirname(os.path.realpath(__file__))
logPath = os.path.join(myPath, "log/race_core.log")
logging.basicConfig(
    # filename=logPath,
    format="%(asctime)s %(levelname)-7s %(message)s",
    datefmt="%Y-%d-%m %H:%M:%S",
    level=logging.DEBUG,
)


class RaceCore:
    def __init__(self, device, server, user, password):
        self.mqtt_server = server
        self.mqtt_user = user
        self.mqtt_password = password
        self.client = None

        self.tracker = LapRFRaceTracker(device)
        self.tracker.on_version.connect(logging.info)

    def mqtt_connect(self):
        logging.info("Connecting to MQTT server %s" % (self.mqtt_server))
        self.client = mqtt.Client()

        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        self.client.username_pw_set(self.mqtt_user, self.mqtt_password)

        self.client.connect(self.mqtt_server, 1883, 60)

    def on_connect(self, client, userdata, flags, rc):
        logging.info("Sucessfully connected to MQTT server with result code" + str(rc))

        #self.client.subscribe("$SYS/#")
        self.client.subscribe("/OpenRace/events")
        # self.client.message_callback_add("/d1ws2812/discovery", self.on_discovery_message)

        self.client.subscribe("/openrace/pilots")
        # self.client.message_callback_add("/openrace/race/start", self.on_race_start)

    def on_message(self, client, userdata, msg):
        logging.debug("Recieved MQTT message: <%s> <%s>" % (msg.topic, msg.payload))

    def run(self):
        self.tracker.request_version()
        while True:
            self.client.loop()
            self.tracker.read_data(stop_if_no_data=True)


@click.command()
@click.option('--device', prompt='Device?', default="/dev/ttyACM0")
def main(device):
    logging.info("starting up")

    rc = RaceCore(device, "10.5.20.35", "openrace", "PASSWORD")
    rc.mqtt_connect()
    rc.run()


if __name__ == '__main__':
    main()
