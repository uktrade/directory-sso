web: python manage.py distributed_migrate --noinput && gunicorn conf.wsgi --bind 0.0.0.0:$PORT
celery_worker: celery worker -A conf -l info
celery_beat: celery beat -A conf -l info -S django
