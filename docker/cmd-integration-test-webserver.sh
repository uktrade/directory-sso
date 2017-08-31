#!/bin/bash -xe

python /usr/src/app/manage.py distributed_migrate --noinput
python /usr/src/app/manage.py create_test_users
python /usr/src/app/manage.py loaddata test_fixtures/load_tests.json
mkdir -p /usr/src/app/sso/static
python /usr/src/app/manage.py collectstatic --noinput
gunicorn config.wsgi --bind [::1]:$PORT --bind 0.0.0.0:$PORT --log-file -
