#!/bin/bash
source /etc/environment
LOCK_FILE=/tmp/chatbot.lck
PHAB_SRC=$PHAB_TOOLS/utilities/src/

# start the chatbot
function start-now()
{
    python ${PHAB_SRC}chat_bot.py --host $PHAB_HOST --last 30 --lock $LOCK_FILE --token $PHAB_MON_TOKEN --type phabtools --config ${PHAB_SRC}default.config
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

