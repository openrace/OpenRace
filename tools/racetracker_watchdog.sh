#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

while true;
do
    if [ -f /tmp/racetracker_watchdog.trigger ];
    then
        echo "$(date): Restarting race_core"
        /bin/bash $DIR/restart_race_core.sh
        rm /tmp/racetracker_watchdog.trigger
        echo -e "$(date): Done\n\n================================================================================\n"
    fi
    sleep 1
done
