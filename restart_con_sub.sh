#!/bin/bash
cd $(dirname $0);

python3 updateSub.py > restart.log

python3 main.py >> restart.log 