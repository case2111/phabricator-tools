#!/bin/bash
BIN=/usr/bin/phabricator-utils-
source /etc/epiphyte.d/environment
for e in $(echo "projects tasks wiki"); do
    $BIN$e | grep "ERROR" | systemd-cat -p err
done
curl $SYNAPSE_LOCAL_URL/shutdown
