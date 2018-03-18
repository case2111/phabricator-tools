#!/bin/bash
BIN=/usr/bin/phab-utilities-
source /etc/epiphyte.d/environment
for e in $(echo "projects tasks wiki"); do
    $BIN$e --env /etc/epiphyte.d/environment | grep "ERROR" | systemd-cat -p err
done
curl $SYNAPSE_LOCAL_URL/shutdown
