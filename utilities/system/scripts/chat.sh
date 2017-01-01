#!/bin/bash
source /etc/environment
LOCK_FILE=/tmp/chatbot.lck.
PHAB_SRC=$PHAB_TOOLS/utilities/src/
BOTS="$PHAB_MON_TOKEN|monitor $PHAB_TASK_TOKEN|prune"

# start the chatbot
function start-now()
{
    git --git-dir $PHAB_TOOLS/.git log -n 1 | grep "^commit" > ${PHAB_TOOLS}/version.txt
    python -u ${PHAB_SRC}chat_bot.py --host $PHAB_HOST --last 30 --lock $LOCK_FILE --monitor $PHAB_MON_TOKEN --prune $PHAB_TASK_TOKEN
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

