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
    |
    | MQTT
    |
  ----------------      MQTT    -----------------------
 | LED controller | -----------| d1ws2812mqtt RGB LEDs |
  ----------------              -----------------------
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
### /OpenRace/events/[request_start, request_stop]
To start and stop races.
### /OpenRace/pilots
To set and get the configured pilots.
### /OpenRace/race/[passing, lastlap, stop]
Race events like pilots passing the finish line and such.
### /OpenRace/settings
Race settings like MW settings, number of laps, minimal lap time ...

## d1ws2812 topics
### /d1ws2812/all
All LED strips are listening on this topic. See the
[d1ws2812 project documentation](https://github.com/oxivanisher/d1ws2812mqtt) for more information.
### /d1ws2812/MAC
Each LED strip is listening to his own topic here. See the
[d1ws2812 project documentation](https://github.com/oxivanisher/d1ws2812mqtt) for more information.


# Manual Setup (Legacy documentation!)

The basis for this project is a  RaspberryPi 3 B+ with a updated [Raspbian](http://www.raspbian.org/).

## Install docker on RaspberryPi
*Based on [freecodecamp.org](https://medium.freecodecamp.org/the-easy-way-to-set-up-docker-on-a-raspberry-pi-7d24ced073ef)*

```bash
curl -fsSL get.docker.com -o get-docker.sh && sh get-docker.sh
sudo groupadd docker
sudo gpasswd -a pi docker
```

Test the setup with:
```bash
docker run hello-world
```

## Configure the RaspberryPi as a access point
*Based on [thepi.io](https://thepi.io/how-to-use-your-raspberry-pi-as-a-wireless-access-point/)*


Install required packages:

```bash
sudo apt install hostapd dnsmasq
```

Stop the services to edit the configuration files:
```bash
sudo systemctl stop hostapd
sudo systemctl stop dnsmasq
```

Configure the RaspberryPis network by editing the file `/etc/dhcpcd.conf`
```bash
sudo nano /etc/dhcpcd.conf
```
and adding the following block at the end
```
interface wlan0
static ip_address=192.168.0.10/24
denyinterfaces eth0
denyinterfaces wlan0
```

Configure the DHCP server (dnsmasq) by editing the file `/etc/dnsmasq.conf`
```bash
sudo mv /etc/dnsmasq.conf /etc/dnsmasq.conf.orig
sudo nano /etc/dnsmasq.conf
```
and add the following block to it
```
interface=wlan0
  dhcp-range=192.168.0.11,192.168.0.30,255.255.255.0,24h
```

Configure the access point (hostapd)
```bash
sudo nano /etc/hostapd/hostapd.conf
```
and add the following block to it
```
interface=wlan0
bridge=br0
hw_mode=g
channel=7
wmm_enabled=0
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_key_mgmt=WPA-PSK
wpa_pairwise=TKIP
rsn_pairwise=CCMP
ssid=OpenRace
wpa_passphrase=PASSWORD
```
**Attention**: You have to change the `PASSWORD` to something only you know. You will have to use the same one for the
d1ws2812mqtt!

Tell hostapd where to find our configuration file by editing its configuration `/etc/default/hostapd`
```bash
sudo nano /etc/default/hostapd
```
file and look for the line `#DAEMON_CONF=””`and change it to:
```
DAEMON_CONF="/etc/hostapd/hostapd.conf"
```

### Optional

The following configuration is only required, if you want to use the RaspberryPis WiFi for internet connectivity over
the LAN cable. For example if you use a tablet or phone (which requires internet) to control the system. OpenRace and
d1ws2812mqtt are not depending on internet access.

Configure traffic forwarding by editing the file `/etc/sysctl.conf`
```bash
sudo nano /etc/sysctl.conf
```
and replace
```
#net.ipv4.ip_forward=1
```
with
```
net.ipv4.ip_forward=1
```

Now you need to add a iptable rule to forward the traffic
```bash
sudo iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
```
and save it to a file
```bash
sudo sh -c "iptables-save > /etc/iptables.ipv4.nat"
```
finall ymake it persistent by adding this in `/etc/rc.local` before the line `exit 0`
```
iptables-restore < /etc/iptables.ipv4.nat
```


Finally, configure the network bridge by first installing `bridge-utils`
```bash
sudo apt install bridge-utils
```
by creating the bridge interface
```bash
sudo brctl addbr br0
```
and connecting the `eth0` interface to the bridge
```bash
sudo brctl addif br0 eth0
```
At last, the bridge needs to be added to the network configuration by editing `/etc/network/interfaces` with
```bash
sudo nano /etc/network/interfaces
```
and adding this block at the end
```
auto br0
iface br0 inet manual
bridge_ports eth0 wlan0
```

To enable the internet up link, reboot your RaspberryPi with
```bash
sudo reboot
```


## Mosquitto
*Based on and using [pascaldevink/rpi-mosquitto](https://github.com/pascaldevink/rpi-mosquitto)*

```bash
docker run -tip 1883:1883 -p 9001:9001 pascaldevink/rpi-mosquitto
```

**Notice:** MQTT should be configured with a password for better security. See the source how to do this.


## Race controller

You have to give the Bluetooth device to the container:
[Source](https://stackoverflow.com/questions/24225647/docker-a-way-to-give-access-to-a-host-usb-or-serial-device/24231872#24231872)

### LapRF

**Notice:** Thanks to Yann Oeffner, we where provided with the official protocol implementation for LapRF. Thank you
very much!

# Questions and answers
* **Q:** Why do you use docker?

  **A:** The aim of this project is, to provide a simple solution to everyone wanting to organize FPV (fun) races.
  Docker makes it easy for everyone to use this project.

* **Q:** Where can I see all DHCP leases?

  **A:** `cat /var/lib/misc/dnsmasq.leases`
