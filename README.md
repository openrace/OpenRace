# OpenRace

OpenRace is a dockerized open source solution to run FPV races. It makes use of MQTT and Python and supports the
immersion RC LapRF tracker as well as fancy RGB LED effects for gates.

The default use case is to deploy this on a RaspberryPi which will talk with the race tracker over Bluetooth and
controls the LED's over WiFi trough MQTT.

It makes use of the following external Projects:
* https://github.com/oxivanisher/d1ws2812mqtt
* https://github.com/fujexo/tbsracetracker
* https://github.com/pascaldevink/rpi-mosquitto

# Module communication matrix
All MQTT connections are running trough the Mosquitto container. But to show the dependencies a little bit better,
some MQTT based connections are presented as direct connections.
```
 ---------------------------                 --------------
| Race controller container |---------------| Race tracker |
 ---------------------------   USB SERIAL    --------------
    |
    | MQTT
    |
 ---------------------     MQTT     -------
| Mosquitto container |------------| WebUi |
 ---------------------              -------
    |                \
    | MQTT            \ MQTT
    |                  \
  ----------------      -----------------------
 | LED controller |    | d1ws2812mqtt RGB LEDs |
  ----------------      -----------------------
```

# Automated setup with ansible
Install requirements:
```bash
sudo apt install git ansible
```
Clone the repository:
```bash
git clone https://github.com/oxivanisher/OpenRace.git
```
Change to the ansible directory
```bash
cd OpenRace/ansible/
```
Run the playbook:
```bash
./run.sh
```
After entering your password for SUDO, the installation continues.

# MQTT Topics
## OpenRace topics
### /OpenRace/events/[request_start, request_stop, request_freeflight, request_led_wave]
To start and stop races.
### /OpenRace/pilots/[ID]/[enabled, frequency, band, channel, name]
To set and get the configured pilots.
### /OpenRace/race/passing/[ID]
The pilot ID passed the gate. The lap time is the message payload.
### /OpenRace/race/[lastlap, start, stop, passing, freeflight]
Race events like pilots passing the finish line and such.
### /OpenRace/race/settings/[amount_laps, min_lap_time_in_seconds, start_delay_in_seconds, race_mw]
Race settings like for the race_core.
### /OpenRace/status/[tracker_voltage, RSSI/1..8, led_strips]
Status information mostly from the race tracker
### /OpenRace/settings/led_control/[start_go_effect, start_countdown_effect, stop_effect, lastlap_effect, passing_wave_delay, wave_color, gate_effect, run_forward_effect, run_backward_effect]
Race settings like for the led_controller.
### /OpenRace/provide/
This topic is for providing information between components.
#### /OpenRace/provide/led_strip_categories
The led_controller provides types of LED strips as a comma separated string. See [LED strip categories table](#led-strip-categories).
#### /OpenRace/provide/tracker_name
The currently active race tracker.
#### /OpenRace/provide/race_mw
The available milliwatt settings like 25, 200, 600 or 800...
### /OpenRace/led/[ID]/category
**Attention:** ID is the MAC address of the LED strip.

Set LED strip category enum: gate, strips_run_forward, strips_run_backward, start_pod, pilot_chip

### /OpenRace/led/[ID]/order
**Attention:** ID is the MAC address of the LED strip.

Set LED strip order


## d1ws2812 topics
### /d1ws2812/all
All LED strips are listening on this topic. See the
[d1ws2812 project documentation](https://github.com/oxivanisher/d1ws2812mqtt) for more information.
### /d1ws2812/[LED strip MAC]
Each LED strip is listening to his own topic here. See the
[d1ws2812 project documentation](https://github.com/oxivanisher/d1ws2812mqtt) for more information.
### /d1ws2812/discovery/[LED strip MAC]
All strips reporting in are publishing here
### /d1ws2812/voltage/[LED strip MAC]
The strips with attached voltage board publish the battery voltage here

# Development environment
By default `docker-compose up` will bring up all the service. To run only selected services via docker-compose one can 
provide the service names together with the `no-deps` flag. Example:
```
docker-compose up --no-deps ui race_core
```
Please keep in mind, that some settings are set to development defaults like the MQTT user and password.

## Pushing cross-platform images
To support both amd64 and arm32v7 we create both images and then create and push a manifest list image as well. The
generation is scripted in `tools/publish_docker_images.sh`. The following configurations might be necessary:
* Logging in to DockerHub to publish images with `docker login`
* Depending on your cli version, you need to enable experimental cli features by adding `"experimental": "enabled"` to
your `~/.docker/config.json`.

### Windows dev environment
For Windows, the Linux Subsystem for Windows is the
easiest way to use this script.  To prepare your Windows, follow the following two Links:
* [Windows Subsystem for Linux Installation Guide for Windows 10](https://docs.microsoft.com/en-us/windows/wsl/install-win10)
* [Installing the Docker client on Windows Subsystem for Linux (Ubuntu)](https://medium.com/@sebagomez/installing-the-docker-client-on-ubuntus-windows-subsystem-for-linux-612b392a44c4)

### Different MQTT
If you like to use another MQTT service/container, you can edit the `src/.env` file.

# Questions and answers
* **Q:** Why do you use docker?

  **A:** The aim of this project is, to provide a simple solution to everyone wanting to organize FPV (fun) races.
  Docker makes it easy for everyone to use this project.

* **Q:** Where can I see all DHCP leases?

  **A:** `cat /var/lib/misc/dnsmasq.leases`

# Tables
## LED strip categories
| Value               | Description                                         |
| ------------------- | --------------------------------------------------- |
| gate                | The strip(s) are ordered as a gate                  |
| strips_run_forward  | The strip(s) are ordered as a line running forward  |
| strips_run_backward | The strip(s) are ordered as a line running backward |
| start_pod           | The strip is used in a start pod for the drones (not yet implemented, somehow the or Freq mus be set) |
| pilot_chip          | The strip is used as a display which pilots ran over the start gate |

## Frequencies, bands and channels
| ID  | Name                            | Frequencies channel 1-8                        |
|---: | ------------------------------- | ---------------------------------------------- |
| 1   | Low Race / Diatone              | 5362, 5399, 5436, 5473, 5510, 5547, 5584, 5621 |
| 2   | IRC / Fatshark / Airwave/ F     | 5740, 5760, 5780, 5800, 5820, 5840, 5860, 5880 |
| 3   | Race Band / r                   | 5658, 5695, 5732, 5769, 5806, 5843, 5880, 5917 |
| 4   | Boscam E Lumenier / DJI / E     | 5705, 5685, 5665, 5645, 5885, 5905, 5925, 5945 |
| 5   | Boscam B                        | 5733, 5752, 5771, 5790, 5809, 5828, 5847, 5866 |
| 6   | Boscam A / Team Black Sheep / A | 5865, 5845, 5825, 5805, 5785, 5765, 5745, 5725 |
| 7   | U                               | 5325, 5348, 5366, 5384, 5402, 5420, 5438, 5456 |
| 8   | O                               | 5474, 5492, 5510 ,5528, 5546, 5564, 5582, 5600 |
| 9   | L                               | 5333, 5373, 5413, 5453, 5493, 5533, 5573, 5613 |
| 10  | Raceband V2 / H                 | 5653, 5693, 5733, 5773, 5813, 5853, 5893, 5933 |
  

The ID is the internally used value in MQTT.

## LapRF Protocol
### Known topics and fields
| Topic     | Field      |
| --------- | ---------- |
| DETECTION | DECODER_ID |
| DETECTION | PILOT_ID
| DETECTION | RTC_TIME
| DETECTION | DETECTION_NUMBER
| DETECTION | DETECTION_PEAK_HEIGHT
| DETECTION | DETECTION_FLAGS
| RF_SETTINGS | PILOT_ID
| RF_SETTINGS | RF_GAIN
| RF_SETTINGS | RF_THRESHOLD
| RF_SETTINGS | RF_ENABLE
| RF_SETTINGS | RF_CHANNEL
| RF_SETTINGS | RF_BAND
| RF_SETTINGS | RF_FREQUENCY
| STATUS      | STATUS_NOISE
| STATUS      | STATUS_INPUT_VOLTAGE
| STATUS      | PILOT_ID
| STATUS      | RSSI_MEAN
| STATUS      | STATUS_COUNT
| STATUS      | STATUS_GATE_STATE
| STATUS      | STATUS_FLAGS
| DESC        | DESC_SYSTEM_VERSION
| DESC        | DESC_PROTOCOL_VERSION
| TIME        | TIME_RTC_TIME
| TIME        | RTC_TIME
| SETTINGS    | SETTINGS_FACTORY_NAME
| NETWORK     | NETWORK_PING
| DATA        | DATA_DUMP
| DATA        | DATA_DUMP_LAST_PACKET
| DATA        | CTRL_REQ_DATA
| DATA        | STATE_CTRL

### Unknown topics and fields
#### Topics
* RSSI
* CALIBRATION_LOG
* RESEND

#### Fields
* STATUS_RSSI
* STATUS_COUNT
* RSSI_MIN
* RSSI_MAX
* RSSI_COUNT
* RSSI_ENABLE
* RSSI_INTERVAL
* RSSI_SDEV
* DETECTION_COUNT_CURRENT
* DETECTION_COUNT_FROM
* DETECTION_COUNT_UNTIL
* RF_ENABLE
* RF_CHANNEL
* RF_THRESHOLD
* RF_GAIN
* CTRL_REQ_RACE
* CTRL_REQ_CAL
* CTRL_REQ_STATIC_CAL
* CALIBRATION_LOG_HEIGHT
* CALIBRATION_LOG_NUM_PEAK
* CALIBRATION_LOG_BASE
* SETTINGS_NAME
* SETTINGS_STATUS_UPDATE_PERIOD
* SETTINGS_RSSI_SAMPLE_PERIOD
* 
* SETTINGS_SAVE_SETTINGS
* SETTINGS_MIN_LAP_TIME
* SETTINGS_ENABLED_MODULES


### Thanks

**Notice:** Thanks to Yann Oeffner, we where provided with parts of the official protocol implementation for LapRF. Thank you
very much!
