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

level = logging.INFO
if os.environ.get("DEBUG", "true").lower() == "true":
    level = logging.DEBUG

myPath = os.path.dirname(os.path.realpath(__file__))
logPath = os.path.join(myPath, "log/race_core.log")
logging.basicConfig(
    # filename=logPath,
    format="%(asctime)s %(levelname)-7s %(message)s",
    datefmt="%Y-%d-%m %H:%M:%S",
    level=level,
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
        self.tracker.on_rf_settings.connect(self.on_rf_settings)
        self.mqtt_connected = False

        self.pilots = {}
        self.race = {}
        self.current_race = 0

        # race settings
        self.race_settings = {
            'amount_laps': 4,
            'min_lap_time_in_seconds': 10,
            'start_delay_in_seconds': 5,
            'race_mw': 25,
        }

        self.milliwatts = [25, 200, 600]

        atexit.register(self.exit_handler)

    def mqtt_connect(self):
        logging.info("Connecting to MQTT server <%s>" % (self.mqtt_server))
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.username_pw_set(self.mqtt_user, self.mqtt_password)
        self.mqtt_client.connect(self.mqtt_server, 1883, 60)

    def on_connect(self, client, userdata, flags, rc):
        logging.info("Sucessfully connected to MQTT server <%s> with result code: %s" % (self.mqtt_server, str(rc)))
        # self.client.subscribe("$SYS/#")

        self.mqtt_client.subscribe("/OpenRace/#")
        self.mqtt_client.message_callback_add("/OpenRace/events/#", self.on_events_message)
        self.mqtt_client.message_callback_add("/OpenRace/pilots/#", self.on_pilots_message)
        # self.mqtt_client.message_callback_add("/OpenRace/race", self.on_race_message)
        self.mqtt_client.message_callback_add("/OpenRace/race/settings/#", self.on_settings_message)

        self.mqtt_connected = True

    # def on_message(self, client, userdata, msg):
    #     logging.debug("Recieved MQTT message: <%s> <%s>" % (msg.topic, msg.payload))

    # internal race methods
    def race_start(self):
        self.mqtt_client.publish("/OpenRace/race/start", self.race_settings['start_delay_in_seconds'], qos=2)
        self.current_race = time.time() + self.race_settings['start_delay_in_seconds']
        self.race[self.current_race] = {}
        self.race[self.current_race]['race_mw'] = self.race_settings['race_mw']
        self.race[self.current_race]['amount_laps'] = self.race_settings['amount_laps']
        self.race[self.current_race]['min_lap_time_in_seconds'] = self.race_settings['min_lap_time_in_seconds']
        self.race[self.current_race]['start_delay_in_seconds'] = self.race_settings['start_delay_in_seconds']
        for pilot in self.pilots.keys():
            self.pilots[pilot].laps = []
            self.pilots[pilot].lastlap = 0
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
            # TODO: implement some kind of ending statistics
        self.race = {}
        self.current_race = 0
        self.tracker.request_stop_race()

    # MQTT Events callback
    def on_events_message(self, client, userdata, msg):
        logging.debug("Recieved MQTT event message: <%s> <%s>" % (msg.topic, msg.payload))

        if msg.topic == '/OpenRace/events/request_start':
            logging.info("Race will start in %s seconds!" % self.race_settings['start_delay_in_seconds'])
            self.race_start()
        elif msg.topic == '/OpenRace/events/request_stop':
            logging.info("Race ended")
            self.race_stop()
        elif msg.topic == '/OpenRace/events/request_freeflight':
            logging.info("Race ending, starting freeflight")
            if self.current_race:
                self.race_stop()
            self.mqtt_client.publish("/OpenRace/race/freeflight", None, qos=2)

        # TODO: handle race timeout (dnf) / max lap time?

    # def on_race_message(self, client, userdata, msg):
    #     logging.debug("OpenRace MQTT race message received: %s" % msg.payload)

    def on_settings_message(self, client, userdata, msg):
        logging.debug("OpenRace MQTT settings message received: <%s> <%s>" % (msg.topic, msg.payload))

        if msg.topic == '/OpenRace/race/settings/amount_laps':
            logging.info("Setting amount of laps to %s" % int(msg.payload))
            self.race_settings['amount_laps'] = int(msg.payload)
        elif msg.topic == '/OpenRace/race/settings/min_lap_time_in_seconds':
            logging.info("Setting minimal lap time to %s" % int(msg.payload))
            self.race_settings['min_lap_time_in_seconds'] = int(msg.payload)
        elif msg.topic == '/OpenRace/race/settings/start_delay_in_seconds':
            logging.info("Setting race start delay %s" % int(msg.payload))
            self.race_settings['start_delay_in_seconds'] = int(msg.payload)
        elif msg.topic == '/OpenRace/race/settings/race_mw':
            logging.info("Setting milli watts to %s" % int(msg.payload))
            self.race_settings['race_mw'] = int(msg.payload)
            self.tracker.milliwatts = int(msg.payload)

    def on_pilots_message(self, client, userdata, msg):
        logging.debug("OpenRace MQTT pilot message received: <%s> <%s>" % (msg.topic, msg.payload))

        field = msg.topic.split('/')[-1]
        id = int(msg.topic.split('/')[-2])

        if id not in self.pilots.keys():
            self.pilots[id] = Pilot()

        if field == 'name':
            self.pilots[id].name = str(msg.payload)
        elif field == 'enabled':
            if self.pilots[id].enabled != int(msg.payload):
                self.pilots[id].enabled = int(msg.payload)
                self.tracker.set_pilot(id, enabled=int(msg.payload))
        elif field == 'frequency':
            if self.pilots[id].frequency != int(msg.payload):
                self.pilots[id].frequency = int(msg.payload)
                self.tracker.set_pilot(id, freq=int(msg.payload))
        elif field == 'band':
            if self.pilots[id].band != int(msg.payload):
                self.pilots[id].band = int(msg.payload)
                self.tracker.set_pilot(id, band=int(msg.payload))
        elif field == 'channel':
            if self.pilots[id].channel != int(msg.payload):
                self.pilots[id].channel = int(msg.payload)
                self.tracker.set_pilot(id, channel=int(msg.payload))

    # RaceTracker Events callback
    def on_pilot_passed(self, pilot_id, seconds):
        now = time.time()

        pilot_name = pilot_id
        if self.pilots[pilot_id].name:
            pilot_name = self.pilots[pilot_id].name

        # check if pilot is configured
        if pilot_id not in self.pilots.keys():
            logging.warning("Unknown Pilot with ID %s detected" % pilot_id)
            return False

        # check if a race is currently happening
        if self.current_race not in self.race.keys():
            # no active race
            lap_time = now - self.pilots[pilot_id].lastlap
            self.mqtt_client.publish("/OpenRace/race/passing/%s" % pilot_id, lap_time, qos=1)
            logging.info("Pilot %s (%s) passed the gate with %s seconds" %
                         (pilot_name, self.pilots[pilot_id].frequency, lap_time))
            self.pilots[pilot_id].lastlap = now

        else:
            # active race

            # check if the pilot went trough the start gate too soon and do not count it
            if self.current_race > 0 and self.current_race > time.time():
                logging.info("Pilot %s (%s) passed too soon!" % (pilot_name, self.pilots[pilot_id].frequency))
                return False

            # check for minimal lap time (and also register the lap time on success)
            if self.pilots[pilot_id].passed():
                lap_time = now - self.pilots[pilot_id].laps[-1]
                if lap_time < 0:
                    lap_time = 0
                # Todo: Use seconds provided by race tracker!
                self.mqtt_client.publish("/OpenRace/race/passing/%s" % pilot_id, lap_time, qos=1)
                logging.info("Pilot %s (%s) passed the gate with %s seconds (%s/%s)" %
                             (pilot_name, self.pilots[pilot_id].frequency, lap_time,
                              len(self.pilots[pilot_id].laps), self.race[self.current_race]['amount_laps']))

                if self.race[self.current_race]['amount_laps'] == len(self.pilots[pilot_id].laps):
                    # race finished
                    race_time = self.pilots[pilot_id].laps[-1] - self.current_race
                    logging.info("Pilot %s finished the race with %s seconds" % (self.pilots[pilot_id].name, race_time))
                elif (self.race[self.current_race]['amount_laps'] - 1) == len(self.pilots[pilot_id].laps):
                    # last lap
                    logging.info("Last lap for pilot %s" % pilot_name)
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
        logging.debug("Status: %s mV | RSSIS %s" % (self.tracker.millivolts, rssis))
        self.mqtt_client.publish("/OpenRace/status/tracker_voltage", self.tracker.millivolts, qos=1)
        for idx, rssi in enumerate(rssis):
            self.mqtt_client.publish("/OpenRace/status/RSSI/%s" % idx, rssi, qos=1)

    def on_rf_settings(self, pilots):
        logging.debug("OpenRace tracker pilot message received: %s" % pilots)
        for pilot in pilots:
            if pilot['id'] not in self.pilots.keys():
                self.pilots[pilot['id']] = Pilot()

            if self.pilots[pilot['id']].enabled != pilot['enabled']:
                self.mqtt_client.publish("/OpenRace/pilots/%s/enabled" % pilot['id'],
                                         pilot['enabled'], qos=1, retain=True)

            if self.pilots[pilot['id']].frequency != pilot['frequency']:
                self.mqtt_client.publish("/OpenRace/pilots/%s/frequency" % pilot['id'],
                                         pilot['frequency'], qos=1, retain=True)

            if self.pilots[pilot['id']].band != pilot['band']:
                self.mqtt_client.publish("/OpenRace/pilots/%s/band" % pilot['id'],
                                         pilot['band'], qos=1, retain=True)

            if self.pilots[pilot['id']].channel != pilot['channel']:
                self.mqtt_client.publish("/OpenRace/pilots/%s/channel" % pilot['id'],
                                         pilot['channel'], qos=1, retain=True)

            # remember: the name is set trough the webinterface or will be get trough the retain message

    def run(self):
        first_run = True

        # MQTT connection
        self.mqtt_connect()
        while not self.mqtt_connected:
            self.mqtt_client.loop()
            time.sleep(0.1)

        # request all pilots
        self.tracker.request_pilots(1, 8)

        pilots_showed = 0
        while True:
            self.mqtt_client.loop()
            self.tracker.read_data(stop_if_no_data=True)

            if first_run:
                # providing infos
                self.mqtt_client.publish("/OpenRace/provide/race_mw",
                                         ",".join(str(mw) for mw in self.milliwatts), qos=1, retain=True)

                # publishing retained race_core settings, after the first loop if there are already
                # retained setting from somewhere else or a earlier run
                self.mqtt_client.publish("/OpenRace/race/settings/amount_laps",
                                         self.race_settings['amount_laps'], qos=1, retain=True)
                self.mqtt_client.publish("/OpenRace/race/settings/min_lap_time_in_seconds",
                                         self.race_settings['min_lap_time_in_seconds'], qos=1, retain=True)
                self.mqtt_client.publish("/OpenRace/race/settings/start_delay_in_seconds",
                                         self.race_settings['start_delay_in_seconds'], qos=1, retain=True)
                self.mqtt_client.publish("/OpenRace/race/settings/race_mw",
                                         self.race_settings['race_mw'], qos=1, retain=True)

                first_run = False

            # show pilots every 60 seconds
            if time.time() - pilots_showed > 60:
                pilots_showed = time.time()

                ret = []
                for pilot in sorted(self.pilots.keys()):
                    if self.pilots[pilot].enabled:
                        ret.append("ID %s; %s" % (pilot, self.pilots[pilot].show()))

                logging.info("Active pilots: %s" % (" | ".join(ret)))

    def exit_handler(self):
        self.race_stop()
        # logging.debug("Removing retained settings")
        # self.mqtt_client.publish("/OpenRace/settings/race_core/amount_laps", None, qos=1, retain=True)
        # self.mqtt_client.publish("/OpenRace/settings/race_core/min_lap_time_in_seconds", None, qos=1, retain=True)
        # self.mqtt_client.publish("/OpenRace/settings/race_core/start_delay_in_seconds", None, qos=1, retain=True)
        # for pilot in self.pilots.keys():
        #     self.mqtt_client.publish("/OpenRace/pilots/%s/enabled" % pilot, None, qos=1, retain=True)
        #     self.mqtt_client.publish("/OpenRace/pilots/%s/frequency" % pilot, None, qos=1, retain=True)
        #     self.mqtt_client.publish("/OpenRace/pilots/%s/band" % pilot, None, qos=1, retain=True)
        #     self.mqtt_client.publish("/OpenRace/pilots/%s/channel" % pilot, None, qos=1, retain=True)


@click.command()
@click.option('--device', prompt='Device?', default="/dev/ttyACM0")
def main(device):
    logging.info("starting up")

    rc = RaceCore(
        LapRFRaceTracker(os.environ.get('TRACKER_DEVICE', device)),
        os.environ.get('MQTT_HOST', "mqtt"),
        os.environ.get('MQTT_USER', "openrace"),
        os.environ.get('MQTT_PASS', "PASSWORD"))
    rc.run()


if __name__ == '__main__':
    main()
