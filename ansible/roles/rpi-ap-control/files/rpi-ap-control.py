#!/usr/bin/env python

# https://raspi.tv/2013/how-to-use-interrupts-with-python-on-the-raspberry-pi-and-rpi-gpio-part-3

import logging
import time
import psutil

import RPi.GPIO as GPIO

logging.basicConfig(level=logging.INFO)


def check_for_hostapd():
    return "hostapd" in (p.name() for p in psutil.process_iter())


class RpiApControl:

    def __init__(self):
        self.led_pin = 23
        self.switch_pin = 24
        self.last_hostapd_check = 0
        self.last_hostapd_state = False
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.led_pin, GPIO.OUT)
        # GPIO 23 (Pin 16) - LED - 330 ohm - gnd

        GPIO.setup(self.switch_pin, GPIO.IN)
        # GPIO 24 (Pin 18) - Switch - 3.3 V
        #                  | 10k ohm - gnd

    def run(self):
        # check if button is pressed
        if GPIO.input(self.switch_pin):
            if check_for_hostapd():
                logging.info("Disabling hostapd")
                # disable hostapd magic
            else:
                logging.info("Enabling hostapd")
                # enable hostapd magic

            for i in range(10):
                GPIO.output(self.led_pin, GPIO.HIGH)
                time.sleep(0.5)
                GPIO.output(self.led_pin, GPIO.LOW)
                time.sleep(0.5)

        # check every 3 seconds if hostapd is running
        if self.last_hostapd_check < time.time() - 3000:
            hostapd_status = check_for_hostapd()
            if hostapd_status:
                GPIO.output(self.led_pin, GPIO.HIGH)
                if not self.last_hostapd_state:
                    logging.info("Hostapd switched on")
            else:
                GPIO.output(self.led_pin, GPIO.LOW)
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
        rac.run()
    except KeyboardInterrupt:
        GPIO.cleanup()
    GPIO.cleanup()