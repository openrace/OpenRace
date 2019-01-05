#!/usr/bin/env python
# vim: set filencoding=utf-8

import logging
import os
import time
import paho.mqtt.client as mqtt
import atexit
import click


level = logging.INFO
if os.environ.get("DEBUG", "true").lower() == "true":
    level = logging.DEBUG

myPath = os.path.dirname(os.path.realpath(__file__))
logPath = os.path.join(myPath, 'log/led_control.log')
logging.basicConfig(
    #filename=logPath,
    format='%(asctime)s %(levelname)-7s %(message)s',
    datefmt='%Y-%d-%m %H:%M:%S',
    level=level)


class LedController:
    def __init__(self, server, user, password):
        self.mqtt_server = server
        self.mqtt_user = user
        self.mqtt_password = password
        self.client = None

        self.led_strips = {}

        self.now = 0
        self.race_start = 0
        self.current_event = None
        self.current_event_payload = None
        self.current_event_control = None
        self.last_led_cleanup = 0
        self.last_status_update = 0

        # module settings
        self.led_settings = {
            'start_go_effect': "6;0;0;255",
            'start_countdown_effect': "6;255;0;0",
            'stop_effect': "6;255;255;255",
            'lastlap_effect': "Z;7;3;100;0;255;255;255;0;0;0",
            'lastlap_gate': "5C:CF:7F:73:01:32", #TODO: this is my own internal testing strip. needs to be removed
        }

        # led strip categories
        self.categories = {
            'start_gates': [],
            'normal_gates': [],
            'strips_run_forward': [],
            'strips_run_backward': []}

        atexit.register(self.exit_handler)

    def mqtt_connect(self):
        logging.info("Connecting to MQTT server <%s>" % (self.mqtt_server))
        self.client = mqtt.Client()

        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        self.client.username_pw_set(self.mqtt_user, self.mqtt_password)

        self.client.connect(self.mqtt_server, 1883, 60)

    def on_connect(self, client, userdata, flags, rc):
        logging.info("Sucessfully connected to MQTT server <%s> with result code: %s" % (self.mqtt_server, str(rc)))

        #self.client.subscribe("$SYS/#")
        self.client.subscribe("/d1ws2812/discovery/#")
        self.client.message_callback_add("/d1ws2812/discovery/#", self.on_discovery_message)

        self.client.subscribe("/OpenRace/race/#")
        self.client.message_callback_add("/OpenRace/race/stop", self.on_race_stop)
        self.client.message_callback_add("/OpenRace/race/start/#", self.on_race_start)
        self.client.message_callback_add("/OpenRace/race/passing/#", self.on_pilot_passing)
        self.client.message_callback_add("/OpenRace/race/lastlap", self.on_last_lap)

        self.client.message_callback_add("/OpenRace/led_category/#", self.on_led_category)

        self.client.message_callback_add("/OpenRace/settings/led_control/#", self.on_settings)

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

    def on_race_stop(self, client, userdata, msg):
        logging.debug("Race is stopping")
        self.current_event = self.race_stop

    def on_last_lap(self, client, userdata, msg):
        logging.debug("Initializing last lap")
        self.current_event = self.last_lap

    def on_led_category(self, client, userdata, msg):
        logging.warning("led category: <%s> <%s>" % (msg.topic, msg.payload))
        # split topic, detect add or remove
        # /OpenRace/led/category/ CATEGORY / add,remove
        # self.categories[category].append()

    def on_settings(self, client, userdata, msg):
        logging.debug("Recieved settings: <%s> <%s>" % (msg.topic, msg.payload))

        if msg.topic == '/OpenRace/settings/led_control/start_go_effect':
            logging.info("Setting start_go_effect to %s" % str(msg.payload))
            self.led_settings['start_go_effect'] = str(msg.payload)
        elif msg.topic == '/OpenRace/settings/led_control/start_countdown_effect':
            logging.info("Setting start_countdown_effect to %s" % str(msg.payload))
            self.led_settings['start_countdown_effect'] = str(msg.payload)
        elif msg.topic == '/OpenRace/settings/led_control/stop_effect':
            logging.info("Setting stop_effect to %s" % str(msg.payload))
            self.led_settings['stop_effect'] = str(msg.payload)
        elif msg.topic == '/OpenRace/settings/led_control/lastlap_effect':
            logging.info("Setting lastlap_effect to %s" % str(msg.payload))
            self.led_settings['lastlap_effect'] = str(msg.payload)
        elif msg.topic == '/OpenRace/settings/led_control/lastlap_gate':
            logging.info("Setting lastlap_gate to %s" % str(msg.payload))
            self.led_settings['lastlap_gate'] = str(msg.payload)

    # internal race methods
    def race_cowntdown(self):
        if self.current_event_payload <= self.now:
            logging.debug("GO! %s" % (time.time() - self.race_start))
            self.current_event = None
            self.client.publish("/d1ws2812/all", self.led_settings['start_go_effect'], qos=1)
        elif (self.current_event_payload - 0.8) <= self.now:
            self.current_event_control = time.time()
        elif (self.now - self.current_event_control) >= 1:
            logging.debug("Wait... %s" % (time.time() - self.race_start))
            self.current_event_control = time.time()
            self.client.publish("/d1ws2812/all", self.led_settings['start_countdown_effect'], qos=1)

    def race_stop(self):
        logging.info("Race stop %s" % (time.time() - self.race_start))
        self.client.publish("/d1ws2812/all", "Z;0", qos=1)
        self.client.publish("/d1ws2812/all", self.led_settings['stop_effect'], qos=1)
        self.current_event = None
        self.race_start = 0

    def last_lap(self):
        logging.info("Last lap! %s" % (time.time() - self.race_start))
        # TODO: implement effect for one start gate and not for all
        for gate in self.led_settings['lastlap_gate'].split(','):
            self.client.publish("/d1ws2812/%s" % gate, self.led_settings['lastlap_effect'], qos=1)
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
        if (self.last_status_update + 60) < self.now:
            self.last_status_update = self.now
            logging.info("Detected LED strips: %s" % len(self.led_strips.keys()))
            self.client.publish("/OpenRace/status/led_strips", len(self.led_strips.keys()))

    def run(self):
        first_run = True
        while True:
            self.now = time.time()
            if self.current_event:
                self.current_event()
            else:
                self.led_cleanup()
                self.status_update()
            self.client.loop()

            if first_run:
                # publishing retained led_control settings, after the first loop if there are already
                # retained setting from somewhere else or a earlier run
                self.client.publish("/OpenRace/settings/led_control/start_go_effect",
                                    self.led_settings['start_go_effect'], qos=1, retain=True)
                self.client.publish("/OpenRace/settings/led_control/start_countdown_effect",
                                    self.led_settings['start_countdown_effect'], qos=1, retain=True)
                self.client.publish("/OpenRace/settings/led_control/stop_effect",
                                    self.led_settings['stop_effect'], qos=1, retain=True)
                self.client.publish("/OpenRace/settings/led_control/lastlap_gate",
                                    self.led_settings['lastlap_gate'], qos=1, retain=True)
                self.client.publish("/OpenRace/settings/led_control/lastlap_effect",
                                    self.led_settings['lastlap_effect'], qos=1, retain=True)
                self.client.publish("/OpenRace/provide/led_strip_categories",
                                    ",".join(str(cat) for cat in self.categories.keys()), qos=1, retain=True)

            first_run = False

    def exit_handler(self):
        pass
        # logging.debug("Removing %s retained discovery messages" % len(self.led_strips))
        # for mac in self.led_strips.keys():
        #     self.client.publish("/d1ws2812/discovery/%s" % mac, None, qos=1, retain=True)


@click.command()
def main():
    logging.info("starting up")

    lc = LedController(os.environ.get('MQTT_HOST', "mqtt"),
                       os.environ.get('MQTT_USER', "openrace"),
                       os.environ.get('MQTT_PASS', "PASSWORD"))
    lc.mqtt_connect()
    lc.run()


if __name__ == '__main__':
    main()
