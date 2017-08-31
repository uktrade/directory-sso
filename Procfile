web: python manage.py distributed_migrate --noinput && mkdir -p sso/static && python manage.py collectstatic --noinput && gunicorn config.wsgi --bind 0.0.0.0:$PORT
