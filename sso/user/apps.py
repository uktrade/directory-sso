from django.apps import AppConfig
from django.db.models.signals import post_delete, post_save

from sso.user import signals


class UserConfig(AppConfig):
    name = 'sso.user'

    def ready(self):
        post_delete.connect(
            receiver=signals.delete_user_cache_by_session,
            sender='sessions.Session'
        )
        post_save.connect(
            receiver=signals.delete_user_cache_by_user,
            sender='user.User'
        )
