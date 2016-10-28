from django.contrib.sessions.models import Session

from rest_framework.generics import RetrieveAPIView

from sso.api.permissions import APIClientPermission
from sso.user.serializers import UserSerializer
from sso.user.models import User


class SessionUserAPIView(RetrieveAPIView):
    permission_classes = [APIClientPermission]
    authentication_classes = []
    serializer_class = UserSerializer

    def get_object(self):
        session_key = self.request.META.get(
            'headers', {}
        ).get('USER-SESSION-KEY')

        session = Session.objects.get(session_key=session_key)

        session_data = session.get_decoded()

        user_id = session_data.get('_auth_user_id')

        return User.objects.get(pk=user_id)
