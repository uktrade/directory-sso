from django.core.management import call_command

from conf.celery import app


@app.task(autoretry_for=(TimeoutError,))
def notify_users():
    call_command('notify_users')


@app.task()
def archive_users():
    call_command('archive_users')


@app.task()
def obsfucate_personal_details():
    call_command('obsfucate_personal_details')
