from django.core.cache import cache
from django.utils import timezone


class UserCache:

    @staticmethod
    def create_session_key(session_key):
        """Return key for caching the user details.

        Arguments:
            session_key {str} -- The `session_key` of the target `Session`.

        """

        return 'session-key-cache-' + session_key

    @staticmethod
    def create_user_session_key(user_id):
        """Return key for caching a list of session keys for a user.

        The list of session keys is stored against the user to allow the
        deletion of the cached sessions upon update of the user.

        Arguments:
            session_key {int} -- The `id` of the target `User`

        """

        return 'user-to-session-key-' + str(user_id)

    @staticmethod
    def serialize_user(user):
        return {'id': user.id, 'email': user.email}

    @classmethod
    def set(cls, user, session):
        """ Store the user details in the cache.

        A user can be logged in on multiple browsers, hence one user can have
        multiple sessions. Each cached sessions must be retrievable via
        `user.id` to allow the cached sessions to be deleted when the user
        details update. Therefore a list of cached session keys are
        stored against the `user.id` - allowing the cached session keys to be
        deleted when the user details update.

        The cached entries will be automatically deleted by the cache when the
        session expires (see `timeout`, below).

        Arguments:
            user {sso.user.User} -- The user to cache against the session key
            session {django.contrib.session.Session} -- the session

        """

        # key for storing the dictionary of user details
        session_key = cls.create_session_key(session.session_key)
        # key for storing a list of session keys
        user_session_key = cls.create_user_session_key(user.id)
        existing_session_keys = cache.get(user_session_key, [])

        # store the details, but invalidate them when the session expires.
        cache.set_many(
            {
                session_key: cls.serialize_user(user),
                user_session_key: existing_session_keys + [session_key],
            },
            timeout=(session.expire_date - timezone.now()).total_seconds()
        )

    @classmethod
    def get(cls, session_key):
        return cache.get(cls.create_session_key(session_key))

    @classmethod
    def delete_by_user_id(cls, user_id):
        """Deletes the cache entries using details known about the user.

        Django does not provide an efficient way to get all sessions for a
        user. For that reason `UserCache.set` stores the session keys against
        the `user.pk`, to allow retrieval and deletion of the sessions using
        the `user.id` - this allowing deletion of the cache entries when the
        user details change.

        Arguments:
            user {sso.user.User} -- The user to delete the cached entries for.

        """

        user_session_key = cls.create_user_session_key(user_id)
        session_keys = cache.get(user_session_key, [])
        cache.delete_many([user_session_key] + session_keys)
