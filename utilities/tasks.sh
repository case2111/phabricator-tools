#!/bin/bash
source /etc/epiphyte.d/environment
source /usr/share/phabricator-tools/functions.sh
_hiddentasks() {
    info_mode "tracking hidden tasks"
    file=${CACHE}hiddenttasks
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

_hiddentasks
