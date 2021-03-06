#!/bin/bash
source /etc/epiphyte.d/environment

INFO_MODE="[INFO]"
CACHE="/var/cache/phabricator-tools/"
HIDDEN_TASKS=${CACHE}hiddentasks
TMP_FILE=${CACHE}taskcache
IDX="index,"
LOG=/var/log/phabricator-cleansing.log

phabricator_encode() {
    _py="
import sys
import urllib.parse

print(urllib.parse.quote(sys.stdin.read()))"
    echo "$@" | python -c "$_py"
}

info_mode() {
    echo "$INFO_MODE $@"
}

_hiddentasks() {
    info_mode "tracking hidden tasks"
    file=$HIDDEN_TASKS
    if [ ! -e "$file" ]; then
        echo "1000" > $file
    fi
    last=$(cat $file)
    next=$last
    for s in $(seq $last $((last+100))); do
        results=$(curl -s $PHAB_HOST/api/maniphest.search \
                        -d api.token=$PHAB_TOKEN \
                        -d constraints[ids][0]=$s)
        if [ -z "$results" ]; then
            break
        else
            echo "$results" | grep -q "PHID-TASK"
            if [ $? -eq 0 ]; then
                next="$s"
            else
                break
            fi
        fi
    done
    if [[ "$next" == "$last" ]]; then
        echo "unchanged task ($last)"
    fi
    echo "$next" > $file
}

_recalc() {
    max=$(cat $HIDDEN_TASKS)
    _pymod="
import sys
import json
r = json.loads(sys.stdin.read())
objs = r['result']['data']
for o in objs:
    f = o['fields']
    i = None
    if 'custom.custom:index' in f:
        i = f['custom.custom:index']
    print('${IDX}{},{}'.format(o['id'], i))"
    count=0
    cmds=""
    current=""
    for s in $(seq 0 $max); do
        count=$((count+1))
        current="$s,$current"
        if [ $count -eq 50 ]; then
            cmds="$current $cmds"
            current=""
            count=0
        fi
    done
    if [ ! -z "$current" ]; then
        cmds="$current $cmds"
    fi
    for s in $(echo "$cmds"); do
        ids=$(echo "$s" | sed 's/^,//g;s/,$//g' | sed "s/,/ /g" | tr ' ' '\n' | sort | awk '{print "-d constraints[ids][" NR-1 "]=" $1}')
        result=$(curl -s $PHAB_HOST/api/maniphest.search \
                    -d api.token=$PHAB_TOKEN \
                    -d queryKey=all $ids)
        if [ ! -z "$result" ]; then
            echo "$result" | grep -q "PHID-TASK"
            if [ $? -eq 0 ]; then
                echo "$result" | python -c "$_pymod" >> $TMP_FILE
            fi
        fi
    done
}

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
                -d transactions[0][value]=$(phabricator_encode "$results") > /dev/null
    fi
}

_tasks() {
    info_mode "$TMP_FILE"
    rm -f $TMP_FILE
    _hiddentasks
    _recalc
}

_run() {
    rpt="dashboard"
    _wikitodash
    dayofweek=$(date +%u)
    if [ $dayofweek -eq 7 ]; then
        info_mode "weekly tasks..."
        rpt="$rpt tasks"
        _tasks
    fi
    echo "done: $rpt" | smirc --report
    curl -s $SYNAPSE_LOCAL_URL/shutdown
}

_run > $LOG 2>&1
cat $LOG | grep -v "INFO" | smirc
exit 0
