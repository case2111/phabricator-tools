#!/bin/bash
source /etc/environment
LOCATION=/opt/phabricator-tools/utilities/tasks/
python ${LOCATION}duedates.py --host $PHAB_HOST --token $PHAB_TOKEN
python ${LOCATION}unmodified.py --host $PHAB_HOST --token $PHAB_TOKEN --room $PHAB_COMMON_ROOM --report 30 --close 45
