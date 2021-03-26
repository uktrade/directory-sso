from django.core.management import call_command

from conf.celery import app


@app.task(autoretry_for=(TimeoutError,))
def notify_users():
    call_command('notify_users')


@app.task()
def archive_users():
    call_command('archive_users')
