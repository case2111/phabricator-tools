#!/bin/bash
source /etc/environment
python ${PHAB_TOOLS}/utilities/src/task_main.py --mode $1
