#!/bin/bash
LOCATION=/opt/phabricator-tools/utilities/api/
python ${LOCATION}duedates.py --host $PHAB_HOST --token $PHAB_TOKEN
python ${LOCATION}unmodified.py --host $PHAB_HOST --token $PHAB_TOKEN --room $PHAB_COMMON_ROOM --report 30 --close 45
