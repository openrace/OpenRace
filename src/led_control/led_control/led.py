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

class LedStrip:
    def __init__(self, mac=None):
        self.mac = mac
        self.category = "gate"
        self.order = -1
        self.time = time.time()
        self.version = None

class LedEvent:
    def __init__(self, target, payload, delay=0.0, comment=""):
        self.target = target
        self.payload = payload
        self.delay = time.time() + delay
        self.comment = comment

    def check(self, grace=0.0):
        if (time.time() + grace) >= self.delay:
            return True
        else:
            return False

class LedController:
    def __init__(self, server, user, password):
        self.mqtt_server = server
        self.mqtt_user = user
        self.mqtt_password = password
        self.client = None

        self.led_strips = []

        self.now = 0.0
        self.race_start = 0.0
        self.last_led_cleanup = 0.0
        self.last_status_update = 0.0
        self.mqtt_loop_block = 2.0

        self.led_events = []

        self.pilots = {}
        self.strip_cells = {}

        # module settings
        self.led_settings = {
            'start_go_effect': "6;0;0;255",
            'start_countdown_effect': "6;255;0;0",
            'stop_effect': "6;255;255;255",
            'lastlap_effect': "Z;7;3;100;0;255;255;255;0;0;0",
            'passing_wave_delay': 0.2,
            'wave_color': "100;100;100",
            'gate_effect': "9;100;10",
            'run_forward_effect': "b;3;100;0;100;30",
            'run_backward_effect': "b;3;100;1;100;30"
        }

        # led strip categories
        self.categories = ['gate', 'strips_run_forward', 'strips_run_backward', 'start_pod', 'pilot_chip']

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
        self.client.subscribe("/d1ws2812/#")
        self.client.message_callback_add("/d1ws2812/discovery/#", self.on_d1ws2812_discovery_message)
        self.client.message_callback_add("/d1ws2812/voltage/#", self.on_d1ws2812_voltage_message)
        self.client.message_callback_add("/d1ws2812/lastwill/#", self.on_d1ws2812_lastwill_message)

        self.client.subscribe("/OpenRace/events/#")
        self.client.message_callback_add("/OpenRace/events/request_led_wave", self.on_request_led_wave)

        self.client.subscribe("/OpenRace/race/#")
        self.client.message_callback_add("/OpenRace/race/stop", self.on_race_stop)
        self.client.message_callback_add("/OpenRace/race/start/#", self.on_race_start)
        self.client.message_callback_add("/OpenRace/race/passing/#", self.on_pilot_passing)
        self.client.message_callback_add("/OpenRace/race/lastlap", self.on_last_lap)
        self.client.message_callback_add("/OpenRace/race/freeflight", self.on_freeflight)

        self.client.subscribe("/OpenRace/pilots/#")
        self.client.message_callback_add("/OpenRace/pilots/+/frequency", self.on_pilot_frequency)

        self.client.subscribe("/OpenRace/led/#")
        self.client.message_callback_add("/OpenRace/led/+/category", self.on_strip_category)
        self.client.message_callback_add("/OpenRace/led/+/order", self.on_strip_order)

        self.client.subscribe("/OpenRace/settings/#")
        self.client.message_callback_add("/OpenRace/settings/led_control/#", self.on_settings)

    def on_d1ws2812_discovery_message(self, client, userdata, msg):
        client_mac = msg.topic.split("/")[-1]
        client_version = msg.payload.decode("utf-8")
        if client_mac not in self.get_strip_macs():
            logging.debug("Discovered <%s> with version <%s>" % (client_mac, client_version))
            self.add_led_event(client_mac, "6;255;0;0")
            strip = LedStrip()
            strip.mac = client_mac
            strip.version = client_version

            max = 0
            for s in self.led_strips:
                if s.order > max:
                    max = s.order
            strip.order = max + 1

            self.led_strips.append(strip)

            # publishing new strips for the frontend
            self.client.publish("/OpenRace/led/%s/category" % strip.mac, strip.category, qos=1, retain=True)
            self.client.publish("/OpenRace/led/%s/order" % strip.mac, strip.order, qos=1, retain=True)

        else:
            strip = self.get_strip(client_mac)

        strip.time = time.time()

    def on_d1ws2812_voltage_message(self, client, userdata, msg):
        client_mac = msg.topic.split("/")[-1]
        client_volt = float(msg.payload.decode("utf-8"))

        if client_mac not in self.strip_cells.keys():
            cells = int(client_volt / 3.5)
            logging.info("Calculated cell count for %s is %s" % (client_mac, cells))
            self.strip_cells[client_mac] = cells

        self.client.publish("/OpenRace/led/%s/voltage" % client_mac, str(client_volt), qos=1, retain=True)

        if client_mac in self.strip_cells.keys():
            cell_voltage = client_volt / self.strip_cells[client_mac]

            if cell_voltage < 3.6:
                self.client.publish("/OpenRace/led/%s/voltage_critical" % client_mac, "true", qos=1, retain=True)
            else:
                self.client.publish("/OpenRace/led/%s/voltage_critical" % client_mac, "false", qos=1, retain=True)

    def on_d1ws2812_lastwill_message(self, client, userdata, msg):
        client_mac = msg.topic.split("/")[-1]
        payload = msg.payload.decode("utf-8")

        if len(payload):
            logging.info("Got last will from strip %s" % client_mac)
            if client_mac in self.strip_cells.keys():
                del self.strip_cells[client_mac]

            self.client.publish("/OpenRace/led/%s/currently_offline" % client_mac, "true", qos=1, retain=True)
        else:
            logging.info("Got last will removal from strip %s" % client_mac)
            self.client.publish("/OpenRace/led/%s/currently_offline" % client_mac, "false", qos=1, retain=True)

    def on_pilot_passing(self, client, userdata, msg):
        pilot_id = int(msg.topic.split("/")[-1])
        frequency = self.pilots[pilot_id]

        logging.debug("Pilot %s with frequency %s passed the gate" % (pilot_id, frequency))
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

        self.led_wave(color, "Pilot passing")

        # ToDo: This might also be depending on strip category.

    def on_pilot_frequency(self, client, userdata, msg):
        pilot_id = int(msg.topic.split("/")[-2])
        try:
            frequency = int(msg.payload)
        except ValueError:
            logging.warning("No frequency was reported for pilot %s" % pilot_id)
            return False
        if pilot_id not in self.pilots.keys():
            self.pilots[pilot_id] = 0
        self.pilots[pilot_id] = frequency
        logging.debug("Setting pilot %s to frequency %s" % (pilot_id, frequency))

    def on_message(self, client, userdata, msg):
        logging.debug("Recieved MQTT message: <%s> <%s>" % (msg.topic, msg.payload.decode("utf-8")))

    # mqtt racing methods
    def on_race_start(self, client, userdata, msg):
        logging.info("Race will start in %s seconds" % float(msg.payload))

        # set default effects for all strip categoreies
        self.set_active_effects(float(msg.payload))

        # setting cowntdown led effects
        self.add_led_event("all", self.led_settings['start_go_effect'], delay=float(msg.payload), comment="GO!")
        for i in range(1, int(msg.payload)):
            self.add_led_event("all", self.led_settings['start_countdown_effect'], delay=float(i),
                               comment="Wait... %s" % ((i - int(msg.payload)) * -1))

    def on_race_stop(self, client, userdata, msg):
        logging.info("Race stopped after %s seconds" % (self.now - self.race_start))
        self.add_led_event("all", "Z;0", comment="Race stop disable LEDs")
        self.add_led_event("all", self.led_settings['stop_effect'], comment="Race stop effect")
        self.race_start = 0

    def on_last_lap(self, client, userdata, msg):
        logging.info("Last lap! %s" % (self.now - self.race_start))

        for strip in self.led_strips:
            # find lowest gates
            min = 999
            for s in self.led_strips:
                if s.order < min and s.category == "gate":
                    min = s.order

            # set all lowest gates to finish gate effect
            for s in self.led_strips:
                if s.order == min and s.category == "gate":
                    self.add_led_event(strip.mac, self.led_settings['lastlap_effect'], comment="Last lap")

    def on_request_led_wave(self, client, userdata, msg):
        logging.info("Emitting LED Wave")
        self.led_wave(self.led_settings['wave_color'], "Manual LED Wave")

    def on_strip_category(self, client, userdata, msg):
        strip_mac = msg.topic.split("/")[-2]
        logging.debug("Recieved LED strip category <%s> for <%s>" % (msg.payload, strip_mac))
        for strip in self.led_strips:
            if strip.mac == strip_mac:
                strip.category = msg.payload.decode("utf-8")

    def on_strip_order(self, client, userdata, msg):
        strip_mac = msg.topic.split("/")[-2]
        logging.debug("Recieved LED strip order <%s> for <%s>" % (msg.payload, strip_mac))
        for strip in self.led_strips:
            if strip.mac == strip_mac:
                strip.order = int(msg.payload)

    def on_freeflight(self, client, userdata, msg):
        logging.info("Starting freeflight mode")

        # set default effects for all strip categoreies
        self.set_active_effects()

        self.led_wave(self.led_settings['wave_color'], "Led wave for start Freeflight")

    def on_settings(self, client, userdata, msg):
        logging.debug("Recieved settings: <%s> <%s>" % (msg.topic, msg.payload))

        if msg.topic == '/OpenRace/settings/led_control/start_go_effect':
            logging.info("Setting start_go_effect to %s" % msg.payload.decode("utf-8"))
            self.led_settings['start_go_effect'] = msg.payload.decode("utf-8")
        elif msg.topic == '/OpenRace/settings/led_control/start_countdown_effect':
            logging.info("Setting start_countdown_effect to %s" % msg.payload.decode("utf-8"))
            self.led_settings['start_countdown_effect'] = msg.payload.decode("utf-8")
        elif msg.topic == '/OpenRace/settings/led_control/stop_effect':
            logging.info("Setting stop_effect to %s" % msg.payload.decode("utf-8"))
            self.led_settings['stop_effect'] = msg.payload.decode("utf-8")
        elif msg.topic == '/OpenRace/settings/led_control/lastlap_effect':
            logging.info("Setting lastlap_effect to %s" % msg.payload.decode("utf-8"))
            self.led_settings['lastlap_effect'] = msg.payload.decode("utf-8")
        elif msg.topic == '/OpenRace/settings/led_control/passing_wave_delay':
            logging.info("Setting passing wave delay to %s" % msg.payload.decode("utf-8"))
            self.led_settings['passing_wave_delay'] = float(msg.payload.decode("utf-8"))
        elif msg.topic == '/OpenRace/settings/led_control/wave_color':
            logging.info("Setting wave_color effect to %s" % msg.payload.decode("utf-8"))
            self.led_settings['wave_color'] = msg.payload.decode("utf-8")
        elif msg.topic == '/OpenRace/settings/led_control/gate_effect':
            logging.info("Setting gate_effect to %s" % msg.payload.decode("utf-8"))
            self.led_settings['gate_effect'] = msg.payload.decode("utf-8")
        elif msg.topic == '/OpenRace/settings/led_control/run_forward_effect':
            logging.info("Setting run_forward_effect to %s" % msg.payload.decode("utf-8"))
            self.led_settings['run_forward_effect'] = msg.payload.decode("utf-8")
        elif msg.topic == '/OpenRace/settings/led_control/run_backward_effect':
            logging.info("Setting run_backward_effect to %s" % msg.payload.decode("utf-8"))
            self.led_settings['run_backward_effect'] = msg.payload.decode("utf-8")

    # internal helper methods
    def led_cleanup(self):
        if (self.last_led_cleanup + 900) < self.now:
            self.last_led_cleanup = self.now
            logging.debug("Cleaning up led strips")
            strips_to_remove = []
            for strip in self.led_strips:
                if (strip.time + 90) < self.now:
                    strips_to_remove.append(strip)
            for strip in strips_to_remove:
                logging.info("Removing LED strip <%s>" % strip.mac)
                self.led_strips.remove(strip)

                self.client.publish("/OpenRace/led/%s/category" % strip.mac, None, qos=1, retain=True)
                self.client.publish("/OpenRace/led/%s/order" % strip.mac, None, qos=1, retain=True)

    def led_wave(self, color, comment):
        for strip in self.led_strips:
            delay = float(strip.order) * self.led_settings['passing_wave_delay']
            if delay < 0:
                delay = 0
            self.add_led_event(strip.mac, "6;%s" % color, delay=delay, comment=comment)

    def set_active_effects(self, delay=0):
        for strip in self.led_strips:
            if strip.category == 'gate':
                self.add_led_event(strip.mac, "Z;%s" % self.led_settings['gate_effect'], delay=delay,
                                   comment="Set default for gates")
            elif strip.category == 'strips_run_forward':
                self.add_led_event(strip.mac, "Z;%s" % self.led_settings['run_forward_effect'], delay=delay,
                                   comment="Set default for strips_run_forward")
            elif strip.category == 'strips_run_backward':
                self.add_led_event(strip.mac, "Z;%s" % self.led_settings['run_backward_effect'], delay=delay,
                                   comment="Set default for run_backward_effect")
            # not yet implemented!
            # 'start_pod', 'pilot_chip'

    def status_update(self):
        if (self.last_status_update + 60) < self.now:
            self.last_status_update = self.now
            logging.info("Detected LED strips: %s" % len(self.led_strips))
            self.client.publish("/OpenRace/status/led_strips", len(self.led_strips))

    def get_strip_macs(self):
        ret = []
        for strip in self.led_strips:
            ret.append(strip.mac)
        return ret

    def get_strip(self, mac):
        ret = None
        for strip in self.led_strips:
            if strip.mac == mac:
                ret = strip
        return ret

    def add_led_event(self, target, payload, delay=0.0, comment=""):
        logging.debug("Adding LED event for <%s> in <%s>: <%s> <%s>" % (target, delay, payload, comment))
        self.led_events.append(LedEvent(target, payload, delay, comment))

    def run(self):
        first_run = True

        while True:
            self.now = time.time()

            block_loop = False

            # self.led_cleanup() # disabling led cleanup, since it should not be required
            self.status_update()

            # LED event handling
            events_to_remove = []
            for event in self.led_events:
                # check if event is overdue
                if event.check():
                    events_to_remove.append(event)
                    self.client.publish("/d1ws2812/%s" % event.target, event.payload, qos=1)
                    logging.debug("LED effect <%s> on <%s>: %s" % (event.payload, event.target, event.comment))
                elif event.check(self.mqtt_loop_block):
                    block_loop = True

            for event in events_to_remove:
                self.led_events.remove(event)

            if not block_loop:
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
                self.client.publish("/OpenRace/settings/led_control/lastlap_effect",
                                    self.led_settings['lastlap_effect'], qos=1, retain=True)
                self.client.publish("/OpenRace/settings/led_control/passing_wave_delay",
                                    self.led_settings['passing_wave_delay'], qos=1, retain=True)
                self.client.publish("/OpenRace/settings/led_control/wave_color",
                                    self.led_settings['wave_color'], qos=1, retain=True)
                self.client.publish("/OpenRace/settings/led_control/gate_effect",
                                    self.led_settings['gate_effect'], qos=1, retain=True)
                self.client.publish("/OpenRace/settings/led_control/run_forward_effect",
                                    self.led_settings['run_forward_effect'], qos=1, retain=True)
                self.client.publish("/OpenRace/settings/led_control/run_backward_effect",
                                    self.led_settings['run_backward_effect'], qos=1, retain=True)
                self.client.publish("/OpenRace/provide/led_strip_categories",
                                    ",".join(self.categories), qos=1, retain=True)

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
