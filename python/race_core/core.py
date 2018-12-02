#!/usr/bin/env python
# vim: set filencoding=utf-8

import logging
import os
import click
import time
import paho.mqtt.client as mqtt
from .common import Pilot


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
    def __init__(self, tracker, server, user, password):
        self.mqtt_server = server
        self.mqtt_user = user
        self.mqtt_password = password
        self.mqtt_client = None

        self.tracker = tracker
        self.tracker.on_version.connect(logging.info)
        self.tracker.on_passing_packet.connect(self.on_pilot_passed)

        self.mqtt_connected = False

        self.pilots = []
        self.band = 2 # currently fatshark hardcoded

    def mqtt_connect(self):
        logging.info("Connecting to MQTT server %s" % (self.mqtt_server))
        self.mqtt_client = mqtt.Client()

        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message

        self.mqtt_client.username_pw_set(self.mqtt_user, self.mqtt_password)

        self.mqtt_client.connect(self.mqtt_server, 1883, 60)

    def on_connect(self, client, userdata, flags, rc):
        logging.info("Sucessfully connected to MQTT server with result code: " + str(rc))
        #self.client.subscribe("$SYS/#")

        self.mqtt_client.subscribe("/OpenRace/#")
        self.mqtt_client.message_callback_add("/OpenRace/events", self.on_events_message)
        self.mqtt_client.message_callback_add("/OpenRace/pilots", self.on_pilots_message)
        self.mqtt_client.message_callback_add("/OpenRace/race", self.on_race_message)
        self.mqtt_client.message_callback_add("/OpenRace/settings", self.on_settings_message)

        self.mqtt_connected = True

    def on_message(self, client, userdata, msg):
        logging.debug("Recieved MQTT message: <%s> <%s>" % (msg.topic, msg.payload))

    # MQTT Events callback
    def on_events_message(self, client, userdata, msg):
        logging.debug("OpenRace MQTT event recieved: %s" % msg.payload)
        if msg.payload == b'start':
            self.tracker.request_start_race()
        elif msg.payload == b'stop':
            self.tracker.request_stop_race()

    def on_pilots_message(self, client, userdata, msg):
        pass

    def on_race_message(self, client, userdata, msg):
        pass

    def on_settings_message(self, client, userdata, msg):
        pass

    # RaceTracker Events callback
    def on_pilot_passed(self):
        debugg.logging("passing packet reached the top")
        pass

    # def on_rf_settings_packet(self):
    #     pass


    # def start_race(self):
    # def end_race(self):
    # def save_settings(self):
    # def get_settings(self):
    # def request_version(self):
    # def pilot_passed(self):


    def run(self):

        # MQTT connection
        self.mqtt_connect()
        while not self.mqtt_connected:
            self.mqtt_client.loop()
            time.sleep(0.1)

        # basic RaceTracker information gathering
        self.tracker.request_version()
        self.tracker.request_time()

        # request all pilots
        for i in range(1, 8):
           self.tracker.request_pilot(i)

        # id, band, freq, gain, channel, enabled, threshold
        # self.tracker.set_pilot(2, 2, 5800, 44, 4, 1, 800)

        while True:
            self.mqtt_client.loop()
            self.tracker.read_data(stop_if_no_data=True)


@click.command()
@click.option('--device', prompt='Device?', default="/dev/ttyACM0")
def main(device):
    logging.info("starting up")

    rc = RaceCore(
        LapRFRaceTracker(device),
        "localhost", "openrace", "PASSWORD")
    rc.run()


if __name__ == '__main__':
    main()
