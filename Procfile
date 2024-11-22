web: python manage.py distributed_migrate --noinput && gunicorn conf.wsgi --bind 0.0.0.0:$PORT
app: python manage.py distributed_migrate --noinput && gunicorn conf.wsgi --bind 0.0.0.0:$PORT
celery_worker: celery -A conf worker -l info
celery_beat: celery -A conf beat -l info -S django
