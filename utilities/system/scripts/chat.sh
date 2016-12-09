#!/bin/bash
source /etc/environment
LOCK_FILE=/tmp/chatbot.lck.
PHAB_SRC=$PHAB_TOOLS/utilities/src/
BOTS="$PHAB_MON_TOKEN|monitor $PHAB_TASK_TOKEN|prune"

# start the chatbot
function start-now()
{
    for bot in $(echo $BOTS); do
        tok=$(echo $bot | cut -d "|" -f 1)
        bot_type=$(echo $bot | cut -d "|" -f 2)
        python ${PHAB_SRC}chat_bot.py --host $PHAB_HOST --last 30 --lock $LOCK_FILE$bot_type --token $tok --type $bot_type &
    done
    running=1
    while [ $running -eq 1 ]; do
        sleep 5
        exists=0
        for bot in $(echo $BOTS | cut -d "|" -f 2); do
            if [ -e $LOCK_FILE$bot ]; then
                exists=1
            fi
        done
        running=$exists
    done
}

# stop the chatbot
function stop-now()
{
    for bot in $(echo $BOTS | cut -d "|" -f 2); do
        rm -f $LOCK_FILE$bot
    done
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

