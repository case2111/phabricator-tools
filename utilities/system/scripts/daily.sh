#!/bin/bash
source /etc/environment
LOCATION=/opt/phabricator-tools/utilities/tasks/
python ${LOCATION}autoclose.py --host $PHAB_HOST --token $PHAB_TOKEN
