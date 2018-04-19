#!/bin/bash
BIN=/usr/bin/phab-utilities-
source /etc/epiphyte.d/environment
cmds="projects wiki"
dayofweek=$(date +%u)
if [ $dayofweek -eq 7 ]; then
    echo "weekly tasks..."
    cmds="$cmds tasks"
fi
for e in $(echo "$cmds"); do
    $BIN$e --env /etc/epiphyte.d/environment 2>&1 | grep -v "INFO" | smirc
done
curl $SYNAPSE_LOCAL_URL/shutdown
echo "done: "$(echo $cmds | sed "s/ /,/g") | smirc --private
