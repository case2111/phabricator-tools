#!/bin/bash
source /etc/environment
LOCK_FILE=/tmp/chatbot.lck

# start the chatbot
function start-now()
{
    python $PHAB_TOOLS/utilities/chatbot/chatty.py --host $PHAB_HOST --last 30 --lock $LOCK_FILE --token $PHAB_MON_TOKEN --type phabtools
}

# stop the chatbot
function stop-now()
{
    rm -f $LOCK_FILE
    sleep 10
}

case $1 in
    "start")
        start-now
        ;;
    "stop")
        stop-now
        ;;
    "restart")
        stop-now
        start-now
        ;;
esac

