#!/bin/bash

if [ -n "$1" ]; then
  exec "$@"
  exit 0
fi

if [[ "$MIGRATE_DB" -eq 1 ]]
then
    echo "MIGRATE_DB Enabled"
    python utility/trunk-player/db_check_create.py
    python manage.py migrate
fi
python manage.py collectstatic --noinput
echo "redis"
redis-server --daemonize yes
echo "nginx"
nginx
echo "daphne"
./manage.py runworker livecall-scan-default > runworker1.log 2>&1 &
./manage.py runworker livecall-scan-default > runworker2.log 2>&1 &
./manage.py runworker livecall-scan-default > runworker3.log 2>&1 &
./manage.py runworker livecall-scan-default > runworker4.log 2>&1 &
daphne trunk_player.asgi:channel_layer --port 7055 --bind 0.0.0.0 --access-log /var/log/trunk-player/daphne_main.log --ping-interval 3 --ping-timeout 12 --proxy-headers
#exec "$@"
