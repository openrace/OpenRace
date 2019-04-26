#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
/usr/bin/install -m 666 -o pi -g pi /dev/null /tmp/racetracker_watchdog.trigger