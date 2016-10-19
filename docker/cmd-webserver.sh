#!/bin/bash -xe

python /usr/src/app/manage.py migrate
mkdir -p /usr/src/app/sso/static
python /usr/src/app/manage.py collectstatic --noinput
gunicorn -c /usr/src/app/gunicorn/conf.py sso.wsgi --bind 0.0.0.0:$PORT --log-file -
