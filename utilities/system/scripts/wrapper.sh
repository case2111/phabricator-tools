#!/bin/bash
source /etc/environment
LOCATION=/opt/phabricator-tools/utilities/
TASKS="tasks"
CALENDAR="calendar"

function run-item()
{
    python ${LOCATION}$1 --host $PHAB_HOST --token $PHAB_TOKEN $2
}

function do-duedates()
{
    run-item "$TASKS/duedates.py" "--mode $1"
}

case $1 in
    "weekly")
    do-duedates 1
    run-item "$TASKS/unmodified.py" "--room $PHAB_COMMON_ROOM --report 30 --close 45"
    ;;
    "daily")
    do-duedates 2
    run-item "$CALENDAR/today.py" "--room $PHAB_BOT_ROOM"
    ;;
esac
