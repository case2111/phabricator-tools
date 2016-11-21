#!/bin/bash
source /etc/environment
LOCATION=/opt/phabricator-tools/utilities/tasks/
function do-duedates()
{
    python ${LOCATION}duedates.py --host $PHAB_HOST --token $PHAB_TOKEN --mode $1
}
case $1 in
    "weekly")
    do-duedates 1
    python ${LOCATION}unmodified.py --host $PHAB_HOST --token $PHAB_TOKEN --room $PHAB_COMMON_ROOM --report 30 --close 45
    ;;
    "daily")
    do-duedates 2
    ;;
esac
