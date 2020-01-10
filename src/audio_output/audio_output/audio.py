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
import hashlib
import subprocess
import wave
import struct
import random

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


class AudioPlayerThread(threading.Thread):

    tmp_path = "/tmp"

    def __init__(self):
        super(AudioPlayerThread, self).__init__()
        logging.info("Initialized audio player thread")
        self.worker_lock = threading.Lock()
        self.play_queue = []
        self.running = True
        signal.signal(signal.SIGALRM, self.sig_timeout_handler)

    @staticmethod
    def hash_text(text):
        h = hashlib.sha1(text.encode('utf-8'))
        return h.hexdigest()

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
        self.running = False
        self.unlock()
        logging.info("Audio player thread terminating")

    def say(self, text, render_only=False):
        hash_text = self.hash_text(text)
        hash_file = os.path.join(AudioPlayerThread.tmp_path, "%s.wav" % hash_text)

        # check if this text was already created as wave and use it if so
        if not os.path.exists(hash_file):
            logging.debug("Rendering wave file for: %s" % text)
            result = subprocess.run([str(x) for x in ["pico2wave", "-w", hash_file, text]], capture_output=True)
            stderr = result.stderr.decode().split('\n')
            stdout = result.stdout.decode().split('\n')
            if len(stderr[0]):
                logging.warning(stderr)
            if len(stdout[0]):
                logging.debug(stdout)

        if not render_only:
            logging.debug("Playing wave file for: %s" % text)
            self.lock()
            self.play_queue.append(hash_file)
            self.unlock()

    def beep(self, frequency, duration, render_only=False):
        hash_file = os.path.join(AudioPlayerThread.tmp_path, "%s-%s.wav" % (frequency, duration))

        # check if this text was already created as wave and use it if so
        # https://soledadpenades.com/posts/2009/fastest-way-to-generate-wav-files-in-python-using-the-wave-module/
        if not os.path.exists(hash_file):
            logging.debug("Rendering beep for frequency %s and duration %s" % (frequency, duration))
            beep_output = wave.open(hash_file, 'w')
            beep_output.setparams((2, 2, 44100, 0, 'NONE', 'not compressed'))

            values = []
            for i in range(0, duration):
                packed_value = struct.pack('h', frequency)
                value = random.randint(-32767, 32767)
                packed_value = struct.pack('h', int(frequency))
                values.append(packed_value)
                values.append(packed_value)

            value_str = ''.join(values)
            beep_output.writeframes(value_str)
            beep_output.close()

        if not render_only:
            logging.debug("Playing beep for frequency %s and duration %s" % (frequency, duration))
            self.lock()
            self.play_queue.append(hash_file)
            self.unlock()

    def run(self):
        while self.running:
            self.lock()
            if len(self.play_queue):
                next_item = self.play_queue.pop(0)
                print("next_item", next_item)
            else:
                next_item = None
            self.unlock()

            if next_item:
                logging.debug("Play file %s" % next_item)
                result = subprocess.run([str(x) for x in ["aplay", next_item]], capture_output=True)
                stderr = result.stderr.decode().split('\n')
                stdout = result.stdout.decode().split('\n')
                if len(stderr[0]):
                    logging.debug(stderr)
                if len(stdout[0]):
                    logging.debug(stdout)


class AudioController(object):
    def __init__(self, server, user, password):
        self.mqtt_server = server
        self.mqtt_user = user
        self.mqtt_password = password
        self.client = None
        self.now = 0.0
        self.race_start = 0.0

        self.audio_worker = AudioPlayerThread()
        self.audio_worker.start()

        self.race_ongoing = False

        self.pilots = {}

        # module settings
        self.audio_settings = {
            'language': "en-US",
            'round_digits': 1,
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
        lap_time = round(float(msg.payload.decode("utf-8")), self.audio_settings['round_digits'])
        if pilot_id in self.pilots.keys():
            pilot_name = self.pilots[pilot_id]
        else:
            pilot_name = "Pilot %s" % pilot_id

        logging.debug("Pilot %s with name %s passed the gate with a laptime of %s" % (pilot_id, pilot_name, lap_time))
        self.audio_worker.say("%s:" % pilot_name)
        self.audio_worker.say("%s" % lap_time)
        # Todo: During races: Also call the lap number?

    def on_pilot_name(self, client, userdata, msg):
        pilot_id = int(msg.topic.split("/")[-2])
        pilot_name = msg.payload.decode("utf-8")

        if pilot_id not in self.pilots.keys():
            self.pilots[pilot_id] = 0
        self.pilots[pilot_id] = pilot_name
        self.audio_worker.say("%s:" % pilot_name, True)
        logging.debug("Setting pilot %s name to %s" % (pilot_id, pilot_name))

    def on_message(self, client, userdata, msg):
        logging.debug("Recieved MQTT message: <%s> <%s>" % (msg.topic, msg.payload.decode("utf-8")))

    # mqtt racing methods
    def on_race_start(self, client, userdata, msg):
        logging.info("The race will start in %s seconds" % float(msg.payload))

        self.race_ongoing = True
        self.race_start = time.time() + float(msg.payload)

        self.audio_worker.say("The race will start in %s seconds" % float(msg.payload))

        # Todo: beep low, beep low, beep low, beeeeep high

    def on_race_stop(self, client, userdata, msg):
        logging.info("Race stopped after %s seconds" % (self.now - self.race_start))
        self.race_ongoing = False
        self.race_start = 0.0
        self.audio_worker.say("Race stopped after %s seconds" % (self.now - self.race_start))

    def on_last_lap(self, client, userdata, msg):
        logging.info("Last lap! %s" % (self.now - self.race_start))
        self.audio_worker.say("Last lap!")

    def on_freeflight(self, client, userdata, msg):
        logging.info("Starting freeflight mode")
        self.audio_worker.say("Free flight mode enabled")

    def on_settings(self, client, userdata, msg):
        logging.debug("Recieved settings: <%s> <%s>" % (msg.topic, msg.payload))

        if msg.topic == '/OpenRace/settings/audio_control/language':
            logging.info("Setting language to %s" % msg.payload.decode("utf-8"))
            self.audio_settings['language'] = msg.payload.decode("utf-8")
        elif msg.topic == '/OpenRace/settings/audio_control/round_digits':
            logging.info("Setting round_digits to %s" % msg.payload.decode("utf-8"))
            self.audio_settings['round_digits'] = msg.payload.decode("utf-8")

    # internal helper methods
    def run(self):
        first_run = True

        # pre render beeps
        # self.audio_worker.beep(450, 200, True)
        # self.audio_worker.beep(800, 400, True)

        while True:
            self.now = time.time()

            block_loop = False

            # Audio event handling
            # events_to_remove = []
            # for event in self.led_events:
            #     # check if event is overdue
            #     if event.check():
            #         events_to_remove.append(event)
            #         self.client.publish("/d1ws2812/%s" % event.target, event.payload, qos=1)
            #         logging.debug("LED effect <%s> on <%s>: %s" % (event.payload, event.target, event.comment))
            #     elif event.check(self.mqtt_loop_block):
            #         block_loop = True
            #
            # for event in events_to_remove:
            #     self.led_events.remove(event)

            if not block_loop:
                self.client.loop()

            if first_run:
                # publishing retained led_control settings, after the first loop if there are already
                # retained setting from somewhere else or a earlier run
                self.client.publish("/OpenRace/settings/audio_output/language",
                                    self.audio_settings['language'], qos=1, retain=True)
                self.client.publish("/OpenRace/settings/audio_output/round_digits",
                                    self.audio_settings['round_digits'], qos=1, retain=True)

            first_run = False

    def exit_handler(self):
        self.audio_worker.terminate()

        # logging.debug("Removing %s retained discovery messages" % len(self.led_strips))
        # for mac in self.led_strips.keys():
        #     self.client.publish("/d1ws2812/discovery/%s" % mac, None, qos=1, retain=True)


@click.command()
def main():
    logging.info("starting up")

    ac = AudioController(os.environ.get('MQTT_HOST', "mqtt"),
                         os.environ.get('MQTT_USER', "openrace"),
                         os.environ.get('MQTT_PASS', "PASSWORD"))
    ac.mqtt_connect()
    ac.run()


if __name__ == '__main__':
    main()
