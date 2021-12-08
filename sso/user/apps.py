from django.apps import AppConfig
from django.db.models.signals import pre_save, post_save


class UserConfig(AppConfig):
    name = 'sso.user'

    def ready(self):
        from sso.user import signals

        pre_save.connect(receiver=signals.create_uuid, sender='user.User')
        post_save.connect(receiver=signals.create_profile, sender='user.User')
