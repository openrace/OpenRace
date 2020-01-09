#!/usr/bin/env python
# vim: set filencoding=utf-8

import logging
import os
import time
import paho.mqtt.client as mqtt
import atexit
import click
import threading
import signal


level = logging.INFO
if os.environ.get("DEBUG", "true").lower() == "true":
    level = logging.DEBUG

myPath = os.path.dirname(os.path.realpath(__file__))
logPath = os.path.join(myPath, 'log/audio_output.log')
logging.basicConfig(
    #filename=logPath,
    format='%(asctime)s %(levelname)-7s %(message)s',
    datefmt='%Y-%d-%m %H:%M:%S',
    level=level)


class AudioPlayerThread(object):
    def __init__(self):
        self.worker_lock = threading.Lock()
        signal.signal(signal.SIGALRM, self.sig_timeout_handler)

    def sig_timeout_handler(self, signum, frame):
        self.logger.warning('Lost connection to MPD server')
        self.unlock()
        self.terminate()

    def lock(self):
        self.worker_lock.acquire()

    def unlock(self):
        if self.worker_lock.locked():
            self.worker_lock.release()

    def terminate(self):
        self.lock()
        self.plugin.fade_in_progress = False
        self.unlock()
        try:
            self.client.close()
            self.client.disconnect()
        except mpd.ConnectionError:
            self.logger.debug("Could not disconnect because we are not connected.")
        except mpd.base.ConnectionError:
            self.logger.debug("Could not disconnect because we are not connected.")
        self.logger.debug("Disconnected, worker exititing")


    def say(self, text):
        pass

    def beep(self, frequency, duration):
        pass


class AudioController(object):
    def __init__(self, server, user, password):
        self.mqtt_server = server
        self.mqtt_user = user
        self.mqtt_password = password
        self.client = None
        self.now = 0.0
        self.race_start = 0.0

        self.audio_worker = AudioPlayerThread()

        self.race_ongoing = False

        self.pilots = {}

        # module settings
        self.audio_settings = {
            'language': "lang here",
        }

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

        self.client.subscribe("/OpenRace/events/#")
        self.client.message_callback_add("/OpenRace/events/request_led_wave", self.on_request_led_wave)

        self.client.subscribe("/OpenRace/race/#")
        self.client.message_callback_add("/OpenRace/race/stop", self.on_race_stop)
        self.client.message_callback_add("/OpenRace/race/start/#", self.on_race_start)
        self.client.message_callback_add("/OpenRace/race/passing/#", self.on_pilot_passing)
        self.client.message_callback_add("/OpenRace/race/lastlap", self.on_last_lap)
        self.client.message_callback_add("/OpenRace/race/freeflight", self.on_freeflight)

        self.client.subscribe("/OpenRace/pilots/#")
        self.client.message_callback_add("/OpenRace/pilots/+/name", self.on_pilot_name)

        self.client.subscribe("/OpenRace/settings/#")
        self.client.message_callback_add("/OpenRace/settings/audio_output/#", self.on_settings)

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

    def on_pilot_name(self, client, userdata, msg):
        pilot_id = int(msg.topic.split("/")[-2])
        pilot_name = msg.payload.decode("utf-8")

        if pilot_id not in self.pilots.keys():
            self.pilots[pilot_id] = 0
        self.pilots[pilot_id] = pilot_name
        logging.debug("Setting pilot %s name to %s" % (pilot_id, pilot_name))

    def on_message(self, client, userdata, msg):
        logging.debug("Recieved MQTT message: <%s> <%s>" % (msg.topic, msg.payload.decode("utf-8")))

    # mqtt racing methods
    def on_race_start(self, client, userdata, msg):
        logging.info("Race will start in %s seconds" % float(msg.payload))

        self.audio_worker.lock()
        self.audio_worker.say("Race will start in %s seconds" % float(msg.payload))
        self.audio_worker.unlock()

        # Todo: beep low, beep low, beep low, beeeeep high

        self.race_ongoing = True
        self.race_start = time.time() + float(msg.payload)

    def on_race_stop(self, client, userdata, msg):
        logging.info("Race stopped after %s seconds" % (self.now - self.race_start))
        self.race_ongoing = False
        self.race_start = 0.0

        self.audio_worker.lock()
        self.audio_worker.say("Race stopped after %s seconds" % (self.now - self.race_start))
        self.audio_worker.unlock()

    def on_last_lap(self, client, userdata, msg):
        logging.info("Last lap! %s" % (self.now - self.race_start))

        self.audio_worker.lock()
        self.audio_worker.say("Last lap!")
        self.audio_worker.unlock()

    def on_freeflight(self, client, userdata, msg):
        logging.info("Starting freeflight mode")

        self.audio_worker.lock()
        self.audio_worker.say("Free flight mode enabled")
        self.audio_worker.unlock()

    def on_settings(self, client, userdata, msg):
        logging.debug("Recieved settings: <%s> <%s>" % (msg.topic, msg.payload))

        if msg.topic == '/OpenRace/settings/audio_control/language':
            logging.info("Setting language to %s" % msg.payload.decode("utf-8"))
            self.audio_settings['language'] = msg.payload.decode("utf-8")

    # internal helper methods
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
                self.client.publish("/OpenRace/settings/audio_output/language",
                                    self.audio_settings['language'], qos=1, retain=True)

            first_run = False

    def exit_handler(self):
        self.audio_worker.terminate()

        # logging.debug("Removing %s retained discovery messages" % len(self.led_strips))
        # for mac in self.led_strips.keys():
        #     self.client.publish("/d1ws2812/discovery/%s" % mac, None, qos=1, retain=True)


@click.command()
def main():
    logging.info("starting up")

    lc = AudioController(os.environ.get('MQTT_HOST', "mqtt"),
                         os.environ.get('MQTT_USER', "openrace"),
                         os.environ.get('MQTT_PASS', "PASSWORD"))
    lc.mqtt_connect()
    lc.run()


if __name__ == '__main__':
    main()
