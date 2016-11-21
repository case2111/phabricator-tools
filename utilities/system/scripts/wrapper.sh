#!/bin/bash
source /etc/environment
LOCATION=/opt/phabricator-tools/utilities/

function run-item()
{
    python ${LOCATION}$1/$2.py --host $PHAB_HOST --token $3 $4
}

function run-task()
{
    run-item "tasks" "$1" "$PHAB_TASK_TOKEN" "$2"
}

function run-mon()
{
    run-item "calendar" "$1" "$PHAB_MON_TOKEN" "$2"
}

function do-duedates()
{
    run-task "duedates" "--mode $1"
}

case $1 in
    "weekly")
    do-duedates 1
    run-task "unmodified" "--room $PHAB_COMMON_ROOM --report 30 --close 45"
    ;;
    "daily")
    do-duedates 2
    run-mon "today.py" "--room $PHAB_BOT_ROOM"
    ;;
esac
