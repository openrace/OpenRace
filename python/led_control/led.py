#!/usr/bin/env python
# vim: set filencoding=utf-8

import logging
import os
import time
import paho.mqtt.client as mqtt

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
        self.current_event = None
        self.current_event_payload = None
        self.current_event_control = None
        self.last_led_cleanup = 0
        self.last_status_update = 0

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
        self.client.subscribe("/d1ws2812/discovery")
        self.client.message_callback_add("/d1ws2812/discovery", self.on_discovery_message)

        self.client.subscribe("/openrace/race/#")
        self.client.message_callback_add("/openrace/race/start", self.on_race_start)

    def on_discovery_message(self, cleint, userdata, msg):
        client_mac = msg.payload.decode("utf-8")
        logging.debug("Discovered <%s>" % client_mac)
        if client_mac not in self.led_strips.keys():
            self.client.publish("/d1ws2812/%s" % client_mac, "6;255;0;0", qos=1)
        self.led_strips[client_mac] = time.time()

    def on_message(self, client, userdata, msg):
        logging.debug("Recieved MQTT message: <%s> <%s>" % (msg.topic, msg.payload))

    # mqtt racing methods
    def on_race_start(self, client, userdata, msg):
        self.current_event = self.check_race
        self.current_event_payload = self.now + float(msg.payload)
        self.current_event_control = self.now - 1.0
        logging.info("Race will start in %s seconds" % int(msg.payload))

    # internal race methods
    def check_race(self):
        if self.current_event_payload <= self.now:
            logging.debug("GO!")
            self.client.publish("/d1ws2812/all", "6;0;255;0", qos=1)
            self.current_event = None
        elif (self.now - self.current_event_control) >= 1.0:
            logging.debug("Wait ...")
            self.client.publish("/d1ws2812/all", "6;255;0;0", qos=1)
            self.current_event_control = self.now

    # internal helper methods
    def led_cleanup(self):
        if (self.last_led_cleanup + 30) < self.now:
            self.last_led_cleanup = self.now
            logging.debug("Cleaning up ledstrips")
            for mac in self.led_strips.keys():
                if (self.led_strips[mac] + 60) < self.now:
                    logging.info("Removing LED strip <%s>" % (mac))
                    del self.led_strips[mac]

    def status_update(self):
        if (self.last_status_update + 10) < self.now:
            self.last_status_update = self.now
            logging.info("LED strips: %s - Pilots: %s" % (len(self.led_strips.keys()), len(self.pilots.keys())))

    def run(self):
        while True:
            self.now = time.time()
            self.client.loop()
            self.led_cleanup()
            self.status_update()
            if self.current_event:
                self.current_event()


if __name__ == "__main__":
    lc = LedController("10.5.20.35", "openrace", "PASSWORD")
    lc.mqtt_connect()
    lc.run()
