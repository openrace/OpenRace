# How to install on a target system using Ansible

## Deploy to Raspberry from Raspperry itself
First ssh to the Pi and sync the git repo to it. After that you can just run `./run.sh` from within the ansible folder.

## RPi AP Control
If you want to use the physical RPi AP control, you will have to solder two switches (with a pull down) and two LEDs.
The following GPIO Pins are used:

| GPIO Pin | Physical Pin | What to connect |
|----------|--------------|-----------------|
| 23       | 16           | AP mode LED +   |
| 24       | 18           | AP mode switch  |
| 27       | 13           | Power LED +     |
| 22       | 15           | Power switch    | 

### How to wire the LEDs
    [GPIO Pin] --- [+ LED -] --- [68 ohm resistor*] --- [GND (RPi pin 6, 9, 14, 20, 25, 30, 34, 39)]  

### How to wire the switches
    [GPIO Pin] -|- [switch] - [3.3 V (RPi pin 1)]
                |- [10k ohm resistor] --- [GND (RPi pin 6, 9, 14, 20, 25, 30, 34, 39)]
    
**Attention:** The resistor values are depending on the LEDs you are using. My setup uses default 3 mm LEDs, with no
resistor for the blue LED and a 47 ohm resistor for the red one (I should have used a 68 ohm, but 47 was the only thing
I had at hand). Since different colors use different voltages, you have to calculate them yourself!
                
### Install RPi AP Control
To install the rpi-ap-control daemon, run the following command:
`ansible-playbook rpi-ap-control.yml`
Only do this, if you really installed the hardware buttons and leds as described in the main Readme. If you install
and enable the daemon without the buttons, your Raspberry Pi will shutdown after 1 minute by itself! If you did
it anyways, you have exactly one minute to access the Raspberry trough SSH or with a USB keyboard and screen, log in and
execute the following commands:
`sudo systemctl disable rpi-ap-control.service` and `sudo systemctl stop rpi-ap-control.service`

# Deploy to Raspberry Pi from a remote Linux machine
`ansible-playbook site.yml --inventory="192.168.1.8," -u pi -k`
