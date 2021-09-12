#!/bin/bash
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
./manage.py runworker > runworker1.log 2>&1 &
./manage.py runworker > runworker2.log 2>&1 &
./manage.py runworker > runworker3.log 2>&1 &
./manage.py runworker > runworker4.log 2>&1 &
daphne trunk_player.asgi:application --port 7055 --bind 127.0.0.1 
#exec "$@"
