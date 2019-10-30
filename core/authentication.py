from rest_framework import authentication, exceptions

from django.contrib.sessions.models import Session
from django.utils import timezone

from sso.user.models import User


class SessionAuthentication(authentication.BaseAuthentication):
    """
    Clients should authenticate by passing the sso session id in the
    "Authorization" HTTP header, prepended with the string "SSO_SESSION_ID ".
    For example:
        Authorization: SSO_SESSION_ID 401f7ac837da42b97f613d789819ff93537bee6a
    """

    message_invalid_session = 'Invalid session id'
    message_bad_format = 'Invalid SSO_SESSION_ID header.'
    keyword = 'SSO_SESSION_ID'

    def authenticate(self, request):
        auth = authentication.get_authorization_header(request).split()
        if not auth or auth[0].decode() != self.keyword:
            return None
        if len(auth) == 1:
            raise exceptions.AuthenticationFailed(self.message_bad_format)
        return self.authenticate_credentials(auth[1].decode())

    def authenticate_credentials(self, session_id):
        user = self.get_user(session_id)
        if not user:
            raise exceptions.AuthenticationFailed(self.message_invalid_session)
        return (user, session_id)

    def authenticate_header(self, request):
        return self.keyword

    def get_user(self, session_key):
        try:
            session = Session.objects.get(
                session_key=session_key,
                expire_date__gt=timezone.now()
            )
        except Session.DoesNotExist:
            return None
        else:
            user_id = session.get_decoded().get('_auth_user_id')
            try:
                return User.objects.get(pk=user_id)
            except User.DoesNotExist:
                return None
