#!/bin/bash
source /etc/environment
LOCATION=$PHAB_TOOLS/utilities/
TASKS="tasks"

function run-item()
{
    python ${LOCATION}$1/$2.py --host $PHAB_HOST --token $3 $4
}

function run-task()
{
    run-item "$TASKS" "$1" "$PHAB_TASK_TOKEN" "$2"
}

function run-mon()
{
    run-item "$1" "$2" "$PHAB_MON_TOKEN" "$3"
}

function do-duedates()
{
    run-task "duedates" "--mode $1"
}

function run-status()
{
    run-item "status" "$1" "$PHAB_STATUS_TOKEN" "$2"
}

function push-status()
{
    run-status "ping" "--room $PHAB_BOT_ROOM --flavor $1"
}

function ping-host()
{
    ping -c 4 $1 -4 2>/dev/null
    if [ $? -ne 0 ]; then
        push-status "$1"
    fi
}

function ping-hosts()
{
    domain=$PHAB_CHECK_DOMAIN
    ping-host $domain
    for d in $(echo $PHAB_CHECK_HOSTS); do
        ping-host $d.$domain
    done
}

case $1 in
    "weekly")
    do-duedates 1
    run-task "unmodified" "--room $PHAB_COMMON_ROOM --report 30 --close 45"
    ;;
    "daily")
    do-duedates 2
    run-mon "calendar" "today" "--room $PHAB_BOT_ROOM"
    run-mon "$TASKS" "onsubscribe" "--room $PHAB_BOT_ROOM --project $PHAB_ADMIN_PROJ"
    ping-hosts
    ;;
esac

push-status "$1"
