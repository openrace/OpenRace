#!/bin/bash

if [ -z ${1+x} ]; then
  echo "Please supply true or false to enable or disable the Raspberry Pi access point."
  exit 1
elif [ "$1" = true ]; then
  echo "Enabling Raspberry Pi wifi access point"
  OPTION="{\"raspberry_ap\": true}"
else
  echo "Disabling Raspberry Pi wifi access point"
  OPTION="{\"raspberry_ap\": false}"
fi

echo "Switching the AP mode in background. Check the output if required in the nohup.out file."
nohup ansible-playbook site.yml -e "${OPTION}" --tags ap
