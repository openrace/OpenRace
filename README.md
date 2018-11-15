# OpenRace
OpenRace is a open source solution to run FPV races. It makes use of MQTT and Python and supports the immersion RC LapRF tracker as well as fancy RGB LED effects for gates.

The defualt usecase is to deploy this on a RaspberryPi which will talk with the race tracker over bluetooth and controls the LEDs over WiFi trough MQTT.

It makes use of the following other Projects:
* https://github.com/oxivanisher/d1ws2812mqtt
* https://github.com/fujexo/tbsracetracker

