#!/bin/bash
cd $(dirname $0);
echo `date +%y%m%d%H%M%S` > restart.log
python3 updateSub.py >> restart.log

python3 main.py >> restart.log 
echo `date +%y%m%d%H%M%S` >> restart.log