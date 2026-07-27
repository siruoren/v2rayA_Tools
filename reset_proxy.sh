#!/bin/bash
cd $(dirname $0);
mkdir -p logs;
echo "START TIME: `date`" > logs/restart.log
python3 delSub.py 2>&1|tee -a logs/restart.log
python3 addSub.py 2>&1|tee -a logs/restart.log
python3 updateSub.py 2>&1|tee -a logs/restart.log

python3 main.py  2>&1|tee -a logs/restart.log 
echo "END TIME: `date`"  >> -a logs/restart.log