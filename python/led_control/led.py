#!/usr/bin/env python
# vim: set filencoding=utf-8

import logging
import os
import paho.mqtt.client as mqtt

myPath = os.path.dirname(os.path.realpath(__file__))
logPath = os.path.join(myPath, 'log/race_core.log')
logging.basicConfig(
    filename=logPath,
    format='%(asctime)s %(levelname)-7s %(message)s',
    datefmt='%Y-%d-%m %H:%M:%S',
    level=logging.DEBUG)


class LedController:
    def __init__(self, server, user, password):
        self.mqtt_server = server
        self.mqtt_user = user
        self.mqtt_password = password
        self.client = None

        self.led_strips = []
        self.pilots = []

    def mqtt_connect(self):
        logging.info("Connecting to MQTT server %s" % (self.mqtt_server))
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        self.client.username_pw_set("openrace", "PASSWORD")

        self.client.connect("10.5.20.35", 1883, 60)

    # The callback for when the client receives a CONNACK response from the server.
    def on_connect(self, userdata, flags, rc):
        logging.info("Sucessfully connected to MQTT server")
        print("Connected with result code " + str(rc))

        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        self.client.subscribe("$SYS/#")

    # The callback for when a PUBLISH message is received from the server.
    def on_message(self, userdata, msg):
        logging.debug("Recieved MQTT message")
        print(msg.topic + " " + str(msg.payload))

    def run(self):
        # Blocking call that processes network traffic, dispatches callbacks and
        # handles reconnecting.
        # Other loop*() functions are available that give a threaded interface and a
        # manual interface.
        self.client.loop_forever()


if __name__ == "__main__":
    lc = LedController("10.5.20.35", "openrace", "PASSWORD")
    lc.mqtt_connect()
    lc.run()
