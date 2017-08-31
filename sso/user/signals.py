from django.conf import settings

from sso.user.helpers import UserCache


def delete_user_cache_by_session(sender, instance, *args, **kwargs):
    if settings.FEATURE_CACHE_ENABLED:
        return

    session_data = instance.get_decoded()
    if session_data and '_auth_user_id' in session_data:
        UserCache.delete_by_user_id(session_data['_auth_user_id'])


def delete_user_cache_by_user(sender, instance, created, *args, **kwargs):
    if settings.FEATURE_CACHE_ENABLED:
        return

    if not created:
        # note we delete the cache entry (rather than updating it) because
        # at this point we do not know when the cache entry should be
        # invalidated.
        UserCache.delete_by_user_id(user_id=instance.id)
