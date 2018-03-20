#!/bin/bash
WORKDIR="/opt/phab/sshkeys"
mkdir -p $WORKDIR
rm -f $WORKDIR/*

source /etc/epiphyte.d/environment
json=$(curl -s $PHAB_HOST/api/user.search \
       -d api.token=$SYNAPSE_PHAB_TOKEN \
       -d queryKey=active)
users=$(echo "$json" | python -c "
import sys
import json

inputs = sys.stdin.read()
j = json.loads(inputs)
for u in j['result']['data']:
	print(u['phid'] + ':' + u['fields']['username'])
")

if [ $? -ne 0 ]; then
	echo "unable to retrieve users" | smirc
	exit 1
fi

for u in $(echo $users); do
	name=$(echo $u | cut -d ":" -f 2)
	phid=$(echo $u | cut -d ":" -f 1)
	p=$(curl -s $PHAB_HOST/api/auth.authorizedkeys \
	         -d api.token=$SYNAPSE_PHAB_TOKEN \
	         -d phids[0]=$phid)
	keys=$(echo $p | python -c "
import sys
import json
inputs = sys.stdin.read()
j = json.loads(inputs)
for k in j['result']['data']:
	print(k)
")
    echo "user: $name ($phid)"
    if [ $? -ne 0 ]; then
        echo "error getting keys" | smirc
        continue
    fi
	if [ -z "$keys" ]; then
		echo "no keys"
		continue
	fi
	echo "found keys: $name"
	path=$WORKDIR/$name
	echo "$keys" > ${path}-keys
done

chmod 666 -R $WORKDIR
