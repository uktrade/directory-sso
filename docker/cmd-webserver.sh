#!/bin/bash -xe

python /usr/src/app/manage.py distributed_migrate --noinput
mkdir -p /usr/src/app/sso/static
python /usr/src/app/manage.py collectstatic --noinput
gunicorn config.wsgi --bind [::1]:$PORT --bind 0.0.0.0:$PORT --log-file -
