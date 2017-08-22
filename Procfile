web:
python manage.py migrate && mkdir -p sso/static &&cpython manage.py collectstatic --noinput && gunicorn config.wsgi --bind 0.0.0.0:$PORT
