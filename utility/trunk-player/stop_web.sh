#!/bin/sh

cd /home/radio/trunk-player

for proc in `echo daphne runworker1 runworker2 runworker3 runworker4 runworker5`
do
  ps=`grep ^$proc running.pid | tail -n1 | cut -d: -f2`
  echo "Stopping PID $ps for $proc"
  kill $ps
done

