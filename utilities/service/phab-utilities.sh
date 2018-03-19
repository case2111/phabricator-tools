#!/bin/bash
BIN=/usr/bin/phab-utilities-
source /etc/epiphyte.d/environment
for e in $(echo "projects tasks wiki"); do
    $BIN$e --env /etc/epiphyte.d/environment 2>&1 | grep -v "INFO" | systemd-cat -p err -t phab-utils
done
curl $SYNAPSE_LOCAL_URL/shutdown
