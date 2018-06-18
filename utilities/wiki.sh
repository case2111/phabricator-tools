#!/bin/bash
source /etc/epiphyte.d/environment
source /usr/share/phabricator-tools/functions
DASH=$(echo "$PHAB_TO_DASH" | cut -d "," -f 1)
WIKI=$(echo "$PHAB_TO_DASH" | cut -d "," -f 2)
results=$(curl -s $PHAB_HOST/api/phriction.document.search \
            -d api.token=$PHAB_TOKEN \
            -d constraints[phids][0]=$WIKI \
            -d attachments[content]=1)
if [ -z "$results" ]; then
    echo "unable to get wiki content"
    exit 1
fi

_segment="
import sys
import json

print(json.loads(sys.stdin.read())['result']['data'][0]['attachments']['content']['content']['raw'])"
results=$(echo "$results" | python -c "$_segment")
curl -s $PHAB_HOST/api/dashboard.panel.edit \
        -d api.token=$PHAB_TOKEN \
        -d objectIdentifier=$DASH \
        -d transactions[0][type]="custom.text" \
        -d transactions[0][value]=$(phabricator_encode "$results")
