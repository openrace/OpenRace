#!/usr/bin/env python3

# https://raspi.tv/2013/how-to-use-interrupts-with-python-on-the-raspberry-pi-and-rpi-gpio-part-3

import logging
import time
import psutil
import subprocess
import sys
import os

import RPi.GPIO as GPIO

logging.basicConfig(level=logging.INFO)


def check_for_hostapd():
    return "hostapd" in (p.name() for p in psutil.process_iter())


def run_command(command, ansible_path):
    logging.info("Calling %s" % " ".join(command))
    subprocess.call(command, cwd=ansible_path)


class RpiApControl:

    def __init__(self):
        self.ap_led_pin = 23
        self.ap_switch_pin = 24
        self.power_led_pin = 27
        self.power_switch_pin = 3
        self.last_hostapd_check = 0
        self.last_hostapd_state = False
        self.accept_shutdown_request_time = time.time() + 30
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.ap_led_pin, GPIO.OUT)
        GPIO.setup(self.power_led_pin, GPIO.OUT)
        # GPIO 23 (Pin 16) - LED - 330 ohm - gnd

        GPIO.setup(self.ap_switch_pin, GPIO.IN)
        GPIO.setup(self.power_switch_pin, GPIO.IN)
        # GPIO 24 (Pin 18) - Switch - 3.3 V
        #                  | 10k ohm - gnd

    def run(self, ansible_path):
        GPIO.output(self.power_led_pin, GPIO.HIGH)
        while True:

            # check if power button is pressed
            if GPIO.input(self.power_switch_pin):
                if time.time() > self.accept_shutdown_request_time:
                    for i in range(5):
                        GPIO.output(self.power_led_pin, GPIO.HIGH)
                        time.sleep(0.1)
                        GPIO.output(self.power_led_pin, GPIO.LOW)
                        time.sleep(0.1)

                run_command(["shutdown", "now", "-h"], ansible_path)

            # check if AP button is pressed
            if GPIO.input(self.ap_switch_pin):
                for i in range(5):
                    GPIO.output(self.ap_led_pin, GPIO.HIGH)
                    time.sleep(0.1)
                    GPIO.output(self.ap_led_pin, GPIO.LOW)
                    time.sleep(0.1)

                if check_for_hostapd():
                    logging.info("Disabling hostapd")
                    task = "{\"raspberry_ap\": false}"
                else:
                    logging.info("Enabling hostapd")
                    task = "{\"raspberry_ap\": true}"

                command = ["/usr/bin/ansible-playbook", os.path.join(ansible_path, "site.yml"), "-e", task, "--tags",
                           "ap"]
                run_command(command, ansible_path)

                for i in range(5):
                    GPIO.output(self.ap_led_pin, GPIO.HIGH)
                    time.sleep(0.1)
                    GPIO.output(self.ap_led_pin, GPIO.LOW)
                    time.sleep(0.1)

            # check every 3 seconds if hostapd is running
            if self.last_hostapd_check < time.time() - 3:
                hostapd_status = check_for_hostapd()
                if hostapd_status:
                    GPIO.output(self.ap_led_pin, GPIO.HIGH)
                    if not self.last_hostapd_state:
                        logging.info("Hostapd switched on")
                else:
                    GPIO.output(self.ap_led_pin, GPIO.LOW)
                    if self.last_hostapd_state:
                        logging.info("Hostapd switched off")

                self.last_hostapd_state = hostapd_status
                self.last_hostapd_check = time.time()

            # don't overload the cpu
            time.sleep(0.1)


if __name__ == '__main__':
    logging.info("Staring rpi-ap-control")
    rac = RpiApControl()
    try:
        rac.run(sys.argv[1])
    except KeyboardInterrupt:
        GPIO.cleanup()
    GPIO.cleanup()
