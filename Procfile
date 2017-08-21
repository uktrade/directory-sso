web:
python /usr/src/app/manage.py migrate && mkdir -p /usr/src/app/sso/static &&cpython /usr/src/app/manage.py collectstatic --noinput && gunicorn config.wsgi --bind 0.0.0.0:$PORT
