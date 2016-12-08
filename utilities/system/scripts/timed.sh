#!/bin/bash
source /etc/environment
python ${PHAB_TOOLS}/utilities/src/task_main.py --mode $1
if [[ $1 == "daily" ]]; then
    rm -f /opt/phab/static/*
fi
