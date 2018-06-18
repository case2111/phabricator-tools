#!/bin/bash
BIN=/usr/bin/phab-utilities-
source /etc/epiphyte.d/environment
source /usr/share/phabricator-tools/functions.sh
cmds="projects wiki"
dayofweek=$(date +%u)
if [ $dayofweek -eq 7 ]; then
    echo "weekly tasks..."
    cmds="$cmds tasks"
fi
for e in $(echo "$cmds"); do
    $BIN$e | grep -v "$INFO_MODE" | smirc
done
curl $SYNAPSE_LOCAL_URL/shutdown
echo "done: "$(echo $cmds | sed "s/ /,/g") | smirc --report
