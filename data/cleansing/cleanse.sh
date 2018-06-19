#!/bin/bash
source /etc/epiphyte.d/environment

INFO_MODE="[INFO]"
CACHE="/var/cache/phabricator-tools/"
HIDDEN_TASKS=${CACHE}hiddentasks
TMP_FILE=${CACHE}taskcache
IDX="index,"

function phabricator_encode() {
    _py="
import sys
import urllib.parse

print(urllib.parse.quote(sys.stdin.read()))"
    echo "$@" | python -c "$_py"
}

function info_mode() {
    echo "$INFO_MODE $@"
}

_notassigned() {
    info_mode "making sure monitoring user is assigned"
    results=$(curl -s $PHAB_HOST/api/project.search \
                -d api.token=$PHAB_TOKEN \
                -d queryKey=active \
                -d attachments[members]=1)
    if [ -z "$results" ]; then
        echo "unable to get projects"
    else
        _py="
import sys
import json

j = json.loads(sys.stdin.read())
count = 0
for p in j['result']['data']:
    count += 1
    found = False
    for m in p['attachments']['members']['members']:
        if m['phid'] == '$PHAB_USER_PHID':
            found = True
            break
    if not found:
        print('missing user assignment: {}'.format(p['fields']['name']))
if count == 0:
    print('no projects found?')"

        echo "$results" | python -c "$_py"
    fi
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
o = r['result']['data'][0]
f = o['fields']
i = None
c = o['fields']
if 'custom.custom:index' in c:
    i = c['custom.custom:index']
print('{},{},{},{},{}'.format(f['dateModified'],o['phid'],f['ownerPHID'], i, f['status']['value']))"
    for s in $(seq 0 $max); do
        result=$(curl -s $PHAB_HOST/api/maniphest.search \
                    -d api.token=$PHAB_TOKEN \
                    -d queryKey=all \
                    -d constraints[ids][0]=$s)
        if [ ! -z "$result" ]; then
            echo "$result" | grep -q "PHID-TASK"
            if [ $? -eq 0 ]; then
                item=$(echo "$result" | python -c "$_pymod")
                item="$IDX$s,$item"
                echo "$item" >> $TMP_FILE
            fi
        fi
    done
}

_unmodified() {
    COMMENT=$(phabricator_encode "task updated due to inactivity")
    PROJECTID=$(echo "$PHAB_UNMODIFIED" | cut -d "," -f 1)
    MONTHS=$(echo "$PHAB_UNMODIFIED" | cut -d "," -f 2)
    old=$(date -d "$MONTHS months ago" +%s)
    for r in $(cat $TMP_FILE | grep -E "(open|actionneeded)$"); do
        mod=$(echo "$r" | cut -d "," -f 3)
        id=$(echo "$r" | cut -d "," -f 4)
        user=$(echo "$r" | cut -d "," -f 5)
        echo "$user" | grep -q "PHID-USER";
        if [ $? -eq 0 ]; then
            continue
        fi
        if [ $mod -lt $old ]; then
            curl -s $PHAB_HOST/api/maniphest.edit \
                -d api.token=$PHAB_TOKEN \
                -d objectIdentifier=$id \
                -d transactions[0][type]="comment" \
                -d transactions[0][value]=$COMMENT \
                -d transactions[1][type]="projects.add" \
                -d transactions[1][value][]=$PROJECTID
        fi
    done
}

_index() {
    t=$(mktemp)
    m=$(cat $TMP_FILE | cut -d "," -f 6 | grep -v "^None$")
    for i in $(echo "$m" | sort -u); do
        echo "| $i | $(echo "$m" | grep "^$i$" | wc -l) |" >> $t
    done
    file=${PHAB_INBOX}indexing.md
    echo "| index | count |" > $file
    echo "| --- | --- |" >> $file
    cat $t | sort >> $file
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
                -d transactions[0][value]=$(phabricator_encode "$results")
    fi
}

_activity() {
    info_mode "building activity"
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

_projects() {
    _notassigned
}

_wiki() {
    _activity
    _wikitodash
}

_tasks() {
    info_mode "$TMP_FILE"
    rm -f $TMP_FILE
    _recalc
    _hiddentask
    _unmodified
    _index
}

_run() {
    rpt="wiki projects"
    _projects
    _wiki
    dayofweek=$(date +%u)
    if [ $dayofweek -eq 7 ]; then
        info_mode "weekly tasks..."
        rpt="$rpt tasks"
        _tasks
    fi
    echo "done: $rpt" | smirc --report
}

_run 2>&1 | grep -v "$INFO_MODE" | smirc
curl -s $SYNAPSE_LOCAL_URL/shutdown
