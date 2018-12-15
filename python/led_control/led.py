#!/usr/bin/env python
# vim: set filencoding=utf-8

import logging
import os
import time
import paho.mqtt.client as mqtt
import atexit

myPath = os.path.dirname(os.path.realpath(__file__))
logPath = os.path.join(myPath, 'log/led_control.log')
logging.basicConfig(
    #filename=logPath,
    format='%(asctime)s %(levelname)-7s %(message)s',
    datefmt='%Y-%d-%m %H:%M:%S',
    level=logging.DEBUG)


class LedController:
    def __init__(self, server, user, password):
        self.mqtt_server = server
        self.mqtt_user = user
        self.mqtt_password = password
        self.client = None

        self.led_strips = {}
        self.pilots = {}

        self.now = 0
        self.race_start = 0
        self.current_event = None
        self.current_event_payload = None
        self.current_event_control = None
        self.last_led_cleanup = 0
        self.last_status_update = 0

        atexit.register(self.exit_handler)

    def mqtt_connect(self):
        logging.info("Connecting to MQTT server %s" % (self.mqtt_server))
        self.client = mqtt.Client()

        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        self.client.username_pw_set(self.mqtt_user, self.mqtt_password)

        self.client.connect(self.mqtt_server, 1883, 60)

    def on_connect(self, client, userdata, flags, rc):
        logging.info("Sucessfully connected to MQTT server with result code " + str(rc))

        #self.client.subscribe("$SYS/#")
        self.client.subscribe("/d1ws2812/discovery/#")
        self.client.message_callback_add("/d1ws2812/discovery/#", self.on_discovery_message)

        # self.client.subscribe("/OpenRace/events/#")

        self.client.subscribe("/OpenRace/race/#")
        self.client.message_callback_add("/OpenRace/race/stop", self.on_race_stop)
        self.client.message_callback_add("/OpenRace/race/start/#", self.on_race_start)
        self.client.message_callback_add("/OpenRace/race/passing/#", self.on_pilot_passing)
        self.client.message_callback_add("/OpenRace/race/lastlap", self.on_last_lap)

    def on_discovery_message(self, client, userdata, msg):
        client_mac = msg.topic.split("/")[-1]
        client_version = msg.payload.decode("utf-8")
        if client_mac not in self.led_strips.keys():
            logging.debug("Discovered <%s> with version <%s>" % (client_mac, client_version))
            self.client.publish("/d1ws2812/%s" % client_mac, "6;255;0;0", qos=1)
        self.led_strips[client_mac] = time.time()

    def on_pilot_passing(self, client, userdata, msg):
        frequency = int(msg.payload)
        logging.debug("Pilot with frequency %s passed the gate %s" % (frequency, (time.time() - self.race_start)))
        # https://github.com/betaflight/betaflight/blob/39ced6bbfefa52a6f605ed6635b7e62105c71672/src/main/io/ledstrip.c

        color = "255;20;147"        # COLOR_DEEP_PINK
        if frequency <= 5672:
            color = "255;255;255"   # COLOR_WHITE
        elif frequency <= 5711:
            color = "255;0;0"       # COLOR_RED
        elif frequency <= 5750:
            color = "255;165;0"     # COLOR_ORANGE
        elif frequency <= 5789:
            color = "255;255;0"     # COLOR_YELLOW
        elif frequency <= 5829:
            color = "0;255;0"       # COLOR_GREEN
        elif frequency <= 5867:
            color = "0;0;255"       # COLOR_BLUE
        elif frequency <= 5906:
            color = "238;130;238"   # COLOR_DARK_VIOLET

        self.client.publish("/d1ws2812/all", "6;%s" % color, qos=1)

    def on_message(self, client, userdata, msg):
        logging.debug("Recieved MQTT message: <%s> <%s>" % (msg.topic, msg.payload))

    # mqtt racing methods
    def on_race_start(self, client, userdata, msg):
        self.race_start = self.now + float(msg.payload)
        self.current_event = self.race_cowntdown
        self.current_event_payload = self.now + float(msg.payload)
        self.current_event_control = self.now - 1.1
        logging.info("Race will start in %s seconds" % int(msg.payload))
        self.client.publish("/d1ws2812/all", "Z;255;0;0", qos=1)

    def on_race_stop(self, client, userdata, msg):
        self.current_event = self.race_stop
        logging.debug("Race is stopping")

    def on_last_lap(self, client, userdata, msg):
        self.current_event = self.last_lap
        logging.debug("Initializing last lap")

    # internal race methods
    def race_cowntdown(self):
        if self.current_event_payload <= self.now:
            logging.debug("GO! %s" % (time.time() - self.race_start))
            self.current_event = None
            self.client.publish("/d1ws2812/all", "6;0;0;255", qos=1)
        elif (self.current_event_payload - 0.8) <= self.now:
            self.current_event_control = time.time()
        elif (self.now - self.current_event_control) >= 1:
            logging.debug("Wait... %s" % (time.time() - self.race_start))
            self.current_event_control = time.time()
            self.client.publish("/d1ws2812/all", "6;255;0;0", qos=1)

    def race_stop(self):
        logging.info("Race stop %s" % (time.time() - self.race_start))
        self.client.publish("/d1ws2812/all", "Z;0", qos=1)
        self.client.loop()
        self.client.publish("/d1ws2812/all", "6;255;255;255", qos=1)
        self.client.loop()
        self.current_event = None
        self.race_start = 0

    def last_lap(self):
        logging.info("Last lap! %s" % (time.time() - self.race_start))
        # TODO: implement one start gate and not for all
        self.client.publish("/d1ws2812/all", "Z;7;3;100;0;255;255;255;0;0;0", qos=1)
        self.client.loop()
        self.client.publish("/d1ws2812/all",   "6;255;255;255", qos=1)
        self.client.loop()
        self.current_event = None

    # internal helper methods
    def led_cleanup(self):
        if (self.last_led_cleanup + 900) < self.now:
            self.last_led_cleanup = self.now
            logging.debug("Cleaning up ledstrips")
            strips_to_remove = []
            for mac in self.led_strips.keys():
                if (self.led_strips[mac] + 90) < self.now:
                    strips_to_remove.append(mac)
            for mac in strips_to_remove:
                logging.info("Removing LED strip <%s>" % (mac))
                del self.led_strips[mac]

    def status_update(self):
        if (self.last_status_update + 30) < self.now:
            self.last_status_update = self.now
            logging.info("LED strips: %s - Pilots: %s" % (len(self.led_strips.keys()), len(self.pilots.keys())))
            self.client.publish("/OpenRace/status/led_strips", len(self.led_strips.keys()))

    def run(self):
        while True:
            self.now = time.time()
            if self.current_event:
                self.current_event()
            else:
                self.led_cleanup()
                self.status_update()
                self.client.loop()

    def exit_handler(self):
        logging.debug("Removing %s retained discovery messages" % len(self.led_strips))
        for mac in self.led_strips.keys():
            self.client.publish("/d1ws2812/discovery/%s" % mac, None, qos=1, retain=True)


if __name__ == "__main__":
    lc = LedController("10.5.20.35", "openrace", "PASSWORD")
    lc.mqtt_connect()
    lc.run()
