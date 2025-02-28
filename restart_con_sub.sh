#!/bin/bash
cd $(dirname $0);
echo "START TIME: `date`" > restart.log
python3 updateSub.py >> restart.log 2>&1

python3 main.py >> restart.log 2>&1
echo "END TIME: `date`"  >> restart.log