#!/usr/bin/env python
# vim: set filencoding=utf-8

import logging
import os
import click
import time
import json
import atexit
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
        self.tracker.on_passing_packet.connect(self.on_pilot_passed)
        self.tracker.on_status_packet.connect(self.on_status_package)
        self.tracker.on_rf_settings.connect(self.on_pilots_message)
        self.mqtt_connected = False

        self.pilots = {}
        self.race = {}
        self.current_race = 0
        self.band = 2  # currently fatshark hardcoded
        # self.startup = time.time()

        # race settings
        self.race_amount_laps = 4
        self.race_min_lap_time = 10
        self.race_start_delay = 5

        atexit.register(self.exit_handler)

    def mqtt_connect(self):
        logging.info("Connecting to MQTT server %s" % (self.mqtt_server))
        self.mqtt_client = mqtt.Client()

        self.mqtt_client.on_connect = self.on_connect
        # self.mqtt_client.on_message = self.on_message

        self.mqtt_client.username_pw_set(self.mqtt_user, self.mqtt_password)

        self.mqtt_client.connect(self.mqtt_server, 1883, 60)

    def on_connect(self, client, userdata, flags, rc):
        logging.info("Sucessfully connected to MQTT server with result code: " + str(rc))
        # self.client.subscribe("$SYS/#")

        self.mqtt_client.subscribe("/OpenRace/#")
        self.mqtt_client.message_callback_add("/OpenRace/events/#", self.on_events_message)
        self.mqtt_client.message_callback_add("/OpenRace/pilots", self.on_pilots_message)
        # self.mqtt_client.message_callback_add("/OpenRace/race", self.on_race_message)
        self.mqtt_client.message_callback_add("/OpenRace/settings/#", self.on_settings_message)

        self.mqtt_connected = True

    # def on_message(self, client, userdata, msg):
    #     logging.debug("Recieved MQTT message: <%s> <%s>" % (msg.topic, msg.payload))

    # internal race methods
    def race_start(self, start_delay):
        self.mqtt_client.publish("/OpenRace/race/start", self.race_start_delay, qos=2)
        self.current_race = time.time() + self.race_start_delay
        self.race[self.current_race] = {}
        self.race[self.current_race]['start_delay'] = self.race_start_delay
        self.race[self.current_race]['amount_laps'] = self.race_amount_laps
        self.race[self.current_race]['min_lap_time'] = self.race_min_lap_time
        for pilot in self.pilots.keys():
            self.pilots[pilot].laps = []
        self.tracker.request_start_race()

    def race_stop(self):
        self.mqtt_client.publish("/OpenRace/race/stop", None, qos=2)

        if self.current_race in self.race.keys():
            self.race[self.current_race]['race_ended'] = time.time()
            self.race[self.current_race]['pilots'] = []
            for pilot in self.pilots.keys():
                if self.pilots[pilot].enabled:
                    self.race[self.current_race]['pilots'].append(self.pilots[pilot].get_stats())
            with open('archive/race_%s.json' % self.current_race, 'w') as fp:
                json.dump(self.race, fp)
        self.race = {}
        self.current_race = 0
        self.tracker.request_stop_race()
        # TODO: implement some kind of ending statistics

    # MQTT Events callback
    def on_events_message(self, client, userdata, msg):
        logging.debug("Recieved MQTT event message: <%s> <%s>" % (msg.topic, msg.payload))

        if msg.topic == '/OpenRace/events/request_start':
            logging.info("Race will start in %s seconds!" % self.race_start_delay)
            self.race_start(int(msg.payload))
        elif msg.topic == '/OpenRace/events/request_stop':
            logging.info("Race ended")
            self.race_stop()

        # TODO: handle race timeout (dnf) / max lap time?

    # def on_race_message(self, client, userdata, msg):
    #     logging.debug("OpenRace MQTT race message received: %s" % msg.payload)

    def on_settings_message(self, client, userdata, msg):
        logging.debug("OpenRace MQTT settings message received: %s" % msg.payload)

        if msg.topic == '/OpenRace/settings/amount_laps':
            logging.info("Setting amount of laps to %s" % int(msg.payload))
            self.race_amount_laps = int(msg.payload)
        elif msg.topic == '/OpenRace/settings/min_lap_time':
            logging.info("Setting minimal lap time to %s" % int(msg.payload))
            self.race_min_lap_time = int(msg.payload)
        elif msg.topic == '/OpenRace/settings/start_delay':
            logging.info("Setting race start delay %s" % int(msg.payload))
            self.race_start_delay = int(msg.payload)

    # RaceTracker Events callback
    def on_pilot_passed(self, pilot_id, seconds):
        # check if pilot is configured
        if pilot_id not in self.pilots.keys():
            logging.warning("Unknown Pilot with ID %s detected" % pilot_id)
            return False

        # check if a race is currently happening
        if self.current_race not in self.race.keys():
            # no active race
            self.mqtt_client.publish("/OpenRace/race/passing", self.pilots[pilot_id].frequency, qos=1)
            logging.info("Pilot %s (%s) passed the gate with %s seconds" %
                         (pilot_id, self.pilots[pilot_id].frequency, seconds))
        else:
            # active race

            # check if the pilot went trough the start gate too soon
            if self.current_race > 0 and self.current_race > time.time():
                logging.info("Pilot %s (%s) passed too soon!" % (pilot_id, self.pilots[pilot_id].frequency))
                return False

            # check for minimal lap time (and also register the laptime on success)
            if self.pilots[pilot_id].passed():
                self.mqtt_client.publish("/OpenRace/race/passing", self.pilots[pilot_id].frequency, qos=1)
                logging.info("Pilot %s (%s) passed the gate with %s seconds (%s/%s)" %
                             (pilot_id, self.pilots[pilot_id].frequency, seconds,
                              len(self.pilots[pilot_id].laps), self.race[self.current_race]['amount_laps']))

                if self.race[self.current_race]['amount_laps'] == len(self.pilots[pilot_id].laps):
                    # race finished
                    logging.info("Pilot %s finished the race" % self.pilots[pilot_id].name)
                elif (self.race[self.current_race]['amount_laps'] - 1) == len(self.pilots[pilot_id].laps):
                    # last lap
                    logging.info("Last lap for pilot %s" % self.pilots[pilot_id].name)
                    self.mqtt_client.publish("/OpenRace/race/lastlap", self.pilots[pilot_id].frequency, qos=1)

                # checking if the race is over
                race_ended = True
                for pilot in self.pilots.keys():
                    if self.pilots[pilot].enabled:
                        # TODO: what happens if someone makes more rounds than the last one?
                        if len(self.pilots[pilot].laps) < self.race[self.current_race]['amount_laps']:
                            race_ended = False
                if race_ended:
                    self.race_stop()

            else:
                logging.debug(
                    'Pilot %s (%s) passed the gate with %s seconds, ignoring due to minimal lap time' % (
                        pilot_id, self.pilots[pilot_id].frequency, seconds))

    def on_status_package(self, rssis):
        # logging.debug("Status: %s mV | RSSIS %s" % (self.tracker.millivolts, rssis))
        self.mqtt_client.publish("/OpenRace/status/tracker_voltage", self.tracker.millivolts, qos=1)
        for idx, rssi in enumerate(rssis):
            self.mqtt_client.publish("/OpenRace/status/RSSI/%s" % idx, rssi, qos=1)

    def on_pilots_message(self, pilots):
        # logging.debug("OpenRace pilot message received: %s" % pilots)
        for pilot in pilots:
            id = pilot['id']
            if id not in self.pilots.keys():
                self.pilots[id] = Pilot()
            self.pilots[id].frequency = pilot['frequency']
            self.pilots[id].enabled = pilot['enabled']

    def run(self):

        # MQTT connection
        self.mqtt_connect()
        while not self.mqtt_connected:
            self.mqtt_client.loop()
            time.sleep(0.1)

        # request all pilots
        self.tracker.request_pilots(1, 8)

        # publishing retained race settings
        self.mqtt_client.publish("/OpenRace/settings/amount_laps", self.race_amount_laps, qos=1, retain=True)
        self.mqtt_client.publish("/OpenRace/settings/min_lap_time", self.race_min_lap_time, qos=1, retain=True)
        self.mqtt_client.publish("/OpenRace/settings/start_delay", self.race_start_delay, qos=1, retain=True)

        pilots_showed = 0
        while True:
            self.mqtt_client.loop()
            self.tracker.read_data(stop_if_no_data=True)

            # show pilots every 10 seconds
            if time.time() - pilots_showed > 30:
                pilots_showed = time.time()

                ret = []
                for pilot in sorted(self.pilots.keys()):
                    if self.pilots[pilot].enabled:
                        ret.append("ID %s; %s" % (pilot, self.pilots[pilot].show()))

                logging.info("Active pilots: %s" % (" | ".join(ret)))

    def exit_handler(self):
        logging.debug("Removing retained settings")
        self.mqtt_client.publish("/OpenRace/settings/amount_laps", None, qos=1, retain=True)
        self.mqtt_client.publish("/OpenRace/settings/min_lap_time", None, qos=1, retain=True)
        self.mqtt_client.publish("/OpenRace/settings/start_delay", None, qos=1, retain=True)


@click.command()
@click.option('--device', prompt='Device?', default="/dev/ttyACM0")
def main(device):
    logging.info("starting up")

    rc = RaceCore(
        LapRFRaceTracker(device),
        "mqtt", "openrace", "PASSWORD")
    rc.run()


if __name__ == '__main__':
    main()
