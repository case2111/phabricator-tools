#!/bin/bash
source /etc/environment
LOCATION=$PHAB_TOOLS/utilities/system/scripts
python ${LOCATION}/main.py --mode $1
