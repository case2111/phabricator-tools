#!/bin/bash
source /etc/environment
curl -s $PHAB_HOST/api/conpherence.updatethread \
    -d api.token="$PHAB_STATUS_TOKEN" \
    -d id=$PHAB_BOT_ROOM \
    -d message="$PHAB_TIMED_MSG $1"
if [[ $1 == "daily" ]]; then
    rm -f /opt/phab/static/*
fi
