#!/bin/bash
source /etc/epiphyte.d/environment
source /usr/share/phabricator-tools/functions.sh
_wikitodash() {
    info_mode "converting wiki to dash"
    DASH=$(echo "$PHAB_TO_DASH" | cut -d "," -f 1)
    WIKI=$(echo "$PHAB_TO_DASH" | cut -d "," -f 2)
    results=$(curl -s $PHAB_HOST/api/phriction.document.search \
                -d api.token=$PHAB_TOKEN \
                -d constraints[phids][0]=$WIKI \
                -d attachments[content]=1)
    if [ -z "$results" ]; then
        echo "unable to get wiki content"
    else
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
    fi
}

_activity() {
    results=$(curl -s $PHAB_HOST/api/user.search \
                -d api.token=$PHAB_TOKEN \
                -d queryKey=active \
                -d constraints[isBot]=0)
    if [ -z "$results" ]; then
        echo "found no users"
    else
        _userpy="
import sys
import json

r = json.loads(sys.stdin.read())['result']['data']
for u in r:
    print('{},{}'.format(u['phid'], u['fields']['username']))"
        _feedpy="
import sys
import json
r = json.loads(sys.stdin.read())['result']
try:
    print(r[next(iter(r))]['epoch'])
except:
    pass"
        users=$(echo "$results" | python -c "$_userpy")
        tmpfile=$(mktemp)
        unknown="unknown"
        for user in $(echo "$users"); do
            u=$(echo "$user" | cut -d "," -f 1)
            feed=$(curl -s $PHAB_HOST/api/feed.query \
                        -d api.token=$PHAB_TOKEN \
                        -d filterPHIDs[0]=$u \
                        -d limit=1)
            dated="$unknown"
            if [ ! -z "$feed" ]; then
                d=$(echo "$feed" | python -c "$_feedpy")
                d=$(date -d @$d +%Y-%m-%d 2>/dev/null)
                if [ ! -z "$d" ]; then
                    dated=$d
                fi
            fi
            echo "| $dated | $(echo $user | cut -d "," -f2) |" >> $tmpfile
        done
        inbox=${PHAB_INBOX}activity.md
        inbox=/tmp/activity.md
        echo "| date | user |" > $inbox
        echo "| ---  | --- |" >> $inbox
        cat $tmpfile | grep -v "$unknown" | sort -r >> $inbox
        cat $tmpfile | grep "$unknown" | sort -r >> $inbox
    fi
}

_activity
_wikitodash
