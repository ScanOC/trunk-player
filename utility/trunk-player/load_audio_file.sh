#!/bin/bash

BASE="/home/myuser"
LOG="$BASE/trunk_player/logs/add_audio.log"

echo "Argument $1" >> $LOG
cd $BASE/trunk_player
. env/bin/activate
./manage.py add_transmission $1 >> $LOG 2>&1

