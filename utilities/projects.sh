#!/bin/bash
source /etc/epiphyte.d/environment

_notassigned() {
    results=$(curl -s $PHAB_HOST/api/project.search \
                -d api.token=$PHAB_TOKEN \
                -d queryKey=active \
                -d attachments[members]=1)
    if [ -z "$results" ]; then
        echo "unable to get projects"
        exit 1
    fi
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
}

_notassigned
