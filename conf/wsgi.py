"""
WSGI config for sso project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

from whitenoise.django import DjangoWhiteNoise


class SetScriptName:
    def __init__(self, application):
        self.application = application

    def __call__(self, environ, start_response):
        environ['SCRIPT_NAME'] = environ.get('HTTP_X_SCRIPT_NAME', '')
        return self.application(environ, start_response)


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "conf.settings")

application = get_wsgi_application()
application = DjangoWhiteNoise(application)
application = SetScriptName(application)
