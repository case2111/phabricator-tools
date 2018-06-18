#!/bin/bash
source /etc/epiphyte.d/environment
source /usr/share/phabricator-tools/functions.sh
HIDDEN_TASKS=${CACHE}hiddentasks
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

_unmodified() {
    COMMENT=$(phabricator_encode "task updated due to inactivity")
    PROJECTID=$(echo "$PHAB_UNMODIFIED" | cut -d "," -f 1)
    MONTHS=$(echo "$PHAB_UNMODIFIED" | cut -d "," -f 2)
    max=$(cat $HIDDEN_TASKS)
    old=$(date -d "$MONTHS months ago" +%s)
    _pymod="
import sys
import json
r = json.loads(sys.stdin.read())
o = r['result']['data'][0]
print('{},{}'.format(o['fields']['dateModified'],o['phid']))"
    for s in $(seq 0 $max); do
        result=$(curl -s $PHAB_HOST/api/maniphest.search \
                    -d api.token=$PHAB_TOKEN \
                    -d queryKey=all \
                    -d constraints[statuses][0]=open \
                    -d constraints[statuses][1]=actionneeded \
                    -d constraints[ids][0]=$s)
        if [ ! -z "$result" ]; then
            echo "$result" | grep -q "PHID-TASK"
            if [ $? -eq 0 ]; then
                item=$(echo "$result" | python -c "$_pymod")
                mod=$(echo "$item" | cut -d "," -f 1)
                id=$(echo "$item" | cut -d "," -f 2)
                if [ $mod -lt $old ]; then
                    curl -s $PHAB_HOST/api/maniphest.edit \
                        -d api.token=$PHAB_TOKEN \
                        -d objectIdentifier=$id \
                        -d transactions[0][type]="comment" \
                        -d transactions[0][value]=$COMMENT \
                        -d transactions[1][type]="projects.add" \
                        -d transactions[1][value]=$PROJECTID
                fi
            fi
        fi
    done
}

_hiddentasks
_unmodified
