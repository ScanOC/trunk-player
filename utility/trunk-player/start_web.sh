#!/bin/sh
# Change to your path
cd /home/radio/trunk_player

. env/bin/activate
ts=`date +%Y%m%d%H%M%S`

cp -f daphne.log daphne.log.$ts
nohup daphne trunk_player.asgi:channel_layer --port 7055 --bind 127.0.0.1 > daphne.log 2>&1 &
d_pid=$!
cp -f runworker.log runworker.log.$ts
cp -f runworker2.log runworker2.log.$ts
cp -f runworker3.log runworker3.log.$ts
cp -f runworker4.log runworker4.log.$ts
nohup ./manage.py runworker > runworker.log 2>&1 &
r_pid=$!
nohup ./manage.py runworker > runworker2.log 2>&1 &
r2_pid=$!
nohup ./manage.py runworker > runworker3.log 2>&1 &
r3_pid=$!
nohup ./manage.py runworker > runworker4.log 2>&1 &
r4_pid=$!
nohup ./manage.py runworker > runworker5.log 2>&1 &
r5_pid=$!


echo "Started $ts" > running.pid
echo "daphne:$d_pid" >> running.pid
echo "runworker1:$r_pid" >> running.pid
echo "runworker2:$r2_pid" >> running.pid
echo "runworker3:$r3_pid" >> running.pid
echo "runworker4:$r4_pid" >> running.pid
echo "runworker5:$r5_pid" >> running.pid
